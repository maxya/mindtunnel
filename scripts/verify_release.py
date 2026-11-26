"""Build and verify allowlisted local archives using preinstalled offline tools."""
import argparse
import gzip
import hashlib
import importlib.metadata
import io
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import venv
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from mindtunnel.files import read_regular
EPOCH = '1795651200'
VERSION = '0.0.1'
DIST = 'mindtunnel-' + VERSION
PACKAGING_CONFIG = b'[egg_info]\ntag_build = \ntag_date = 0\n\n'
GENERATED = {'PKG-INFO', 'setup.cfg', 'mindtunnel.egg-info/PKG-INFO',
             'mindtunnel.egg-info/SOURCES.txt', 'mindtunnel.egg-info/dependency_links.txt',
             'mindtunnel.egg-info/entry_points.txt', 'mindtunnel.egg-info/top_level.txt'}


def manifest():
    names = read_regular(ROOT/'harness/release-files.txt', 65536).decode('utf-8').splitlines()
    if len(names) != len(set(names)) or any(not safe_name(name) for name in names):
        raise ValueError('invalid_release_manifest')
    return names


def safe_name(name):
    path = PurePosixPath(name)
    return bool(path.parts) and not path.is_absolute() and '..' not in path.parts and '\\' not in name


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def run(command, directory, environment):
    result = subprocess.run(command, cwd=directory, env=environment, capture_output=True, timeout=120)
    if result.returncode:
        raise ValueError('verification_command_failed: ' + ' '.join(command[:3]))
    return result.stdout


def build(source, output, environment):
    # Seed canonical backend metadata before SOURCES.txt is first calculated.
    configuration = source/'setup.cfg'
    if configuration.exists() and configuration.read_bytes() != PACKAGING_CONFIG:
        raise ValueError('unexpected_packaging_configuration')
    configuration.write_bytes(PACKAGING_CONFIG)
    os.utime(configuration, (int(EPOCH), int(EPOCH)))
    output.mkdir()
    code = ('import setuptools.build_meta as backend; '
            'backend.build_wheel(' + repr(str(output)) + '); '
            'backend.build_sdist(' + repr(str(output)) + ')')
    run([sys.executable, '-I', '-c', code], source, environment)
    return next(output.glob('*.whl')), next(output.glob('*.tar.gz'))


def wheel_inputs(source_bytes):
    expected = {name:raw for name, raw in source_bytes.items()
                if name.endswith('.py') and name.split('/')[0].startswith('mindtunnel')}
    assets = {'examples/':'examples/', 'schemas/':'schemas/', 'tests/fixtures/':'conformance/'}
    for name, raw in source_bytes.items():
        for prefix, destination in assets.items():
            if name.startswith(prefix):
                target = DIST + '.data/data/share/mindtunnel/' + destination + name[len(prefix):]
                expected[target] = raw
    expected[DIST+'.dist-info/licenses/LICENSE-NOTES.md'] = source_bytes['LICENSE-NOTES.md']
    return expected


def inspect_wheel(path, source_bytes):
    expected = wheel_inputs(source_bytes)
    metadata = {DIST+'.dist-info/'+name for name in
                ('METADATA','WHEEL','entry_points.txt','top_level.txt','RECORD')}
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or set(names) != set(expected) | metadata:
            raise ValueError('unexpected_wheel_member')
        content = {}
        for name in names:
            if not safe_name(name):
                raise ValueError('unsafe_wheel_member')
            mode = archive.getinfo(name).external_attr >> 16
            if stat.S_IFMT(mode) not in (0, stat.S_IFREG):
                raise ValueError('nonregular_wheel_member')
            raw = archive.read(name)
            if name in expected and raw != expected[name]:
                raise ValueError('wheel_content_mismatch')
            content[name] = digest(raw)
    return content


def inspect_sdist(path, source_bytes):
    content = {}
    allowed_directories = {'.'}
    for name in set(source_bytes) | GENERATED:
        allowed_directories.update(parent.as_posix() for parent in PurePosixPath(name).parents)
    with tarfile.open(path, 'r:gz') as archive:
        for member in archive.getmembers():
            relative = PurePosixPath(member.name).relative_to(DIST).as_posix()
            if member.isdir():
                if relative not in allowed_directories:
                    raise ValueError('unexpected_sdist_directory')
                continue
            if not member.isfile() or not safe_name(relative) or relative in content:
                raise ValueError('unsafe_sdist_member')
            if relative not in source_bytes and relative not in GENERATED:
                raise ValueError('unexpected_sdist_member')
            raw = archive.extractfile(member).read()
            if relative == 'setup.cfg' and raw != PACKAGING_CONFIG:
                raise ValueError('unexpected_packaging_configuration')
            if relative in source_bytes and raw != source_bytes[relative]:
                raise ValueError('sdist_content_mismatch')
            content[relative] = digest(raw)
    if not set(source_bytes).issubset(content):
        raise ValueError('missing_sdist_source')
    return content


def normalize_sdist(path):
    """Normalize an already allowlist-verified archive using a fixed epoch and order."""
    entries = []
    with tarfile.open(path, 'r:gz') as archive:
        for member in archive.getmembers():
            raw = b'' if member.isdir() else archive.extractfile(member).read()
            entries.append((member.name, member.isdir(), member.mode, raw))
    buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=buffer, mode='wb', filename='', mtime=int(EPOCH), compresslevel=9) as compressed:
        with tarfile.open(fileobj=compressed, mode='w', format=tarfile.PAX_FORMAT) as archive:
            for name, directory, mode, raw in sorted(entries):
                member = tarfile.TarInfo(name)
                member.type = tarfile.DIRTYPE if directory else tarfile.REGTYPE
                member.mode = mode
                member.mtime = int(EPOCH)
                member.uid = member.gid = 0
                member.uname = member.gname = ''
                member.size = 0 if directory else len(raw)
                archive.addfile(member, None if directory else io.BytesIO(raw))
    path.write_bytes(buffer.getvalue())


def unpack_sdist(path, destination):
    destination.mkdir()
    with tarfile.open(path, 'r:gz') as archive:
        for member in archive.getmembers():
            relative = PurePosixPath(member.name).relative_to(DIST)
            if member.isdir():
                continue
            if not member.isfile() or not safe_name(relative.as_posix()):
                raise ValueError('unsafe_sdist_member')
            target = destination.joinpath(*relative.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.extractfile(member).read())


def installed_checks(wheel, directory, uv, environment):
    directory.mkdir()
    virtual = directory/'venv'
    venv.EnvBuilder(with_pip=False).create(virtual)
    python = virtual/'bin/python'
    command = [uv, '--no-config', 'pip', 'install', '--python', str(python),
               '--offline', '--no-index', '--no-python-downloads', '--no-build-isolation',
               '--no-deps', '--cache-dir', str(directory/'cache'), str(wheel)]
    run(command, directory, environment)
    outside = directory/'outside'
    outside.mkdir()
    code = ('import pathlib,sys,mindtunnel,importlib.metadata as metadata; '
            'assert mindtunnel.__version__ == metadata.version("mindtunnel") == "0.0.1"; '
            'assert metadata.requires("mindtunnel") in (None,[]); '
            'assert pathlib.Path(mindtunnel.__file__).is_relative_to(pathlib.Path(sys.prefix)); '
            'assert not sys.path[0] == ""')
    run([str(python), '-I', '-c', code], outside, environment)
    assets = virtual/'share/mindtunnel'
    result = outside/'result.json'
    report = outside/'report.txt'
    request = outside/'public.json'
    binary = virtual/'bin/mindtunnel'
    raw = run([str(binary), 'request', '--contract', str(assets/'examples/contract.json'),
               '--task', 'Sum amount_cents by category'], outside, environment)
    request.write_bytes(raw)
    run([str(binary), 'run', '--contract', str(assets/'examples/contract.json'),
         '--mapping', str(assets/'examples/mapping.json'), '--data', str(assets/'examples/transactions.csv'),
         '--plan', str(assets/'examples/plan.json'), '--out', str(result)], outside, environment)
    if json.loads(result.read_bytes()) != json.loads((assets/'examples/expected.json').read_bytes()):
        raise ValueError('installed_demo_mismatch')
    run([str(binary), 'report', '--result', str(result), '--out', str(report)], outside, environment)
    if report.read_bytes() != b'group | value\n"food" | 2200\n"transport" | 3000\n':
        raise ValueError('installed_report_mismatch')
    run([str(virtual/'bin/mindtunnel-planner'), 'preview', '--request', str(request)], outside, environment)
    schemas = list((assets/'schemas').glob('*.json'))
    if len(schemas) != 3:
        raise ValueError('missing_installed_schemas')
    for path in schemas:
        json.loads(path.read_bytes())
    vectors = json.loads((assets/'conformance/conformance-v1.json').read_bytes())
    code = ('from mindtunnel.core import load,parse,validate,Invalid; import json,sys; '
            'c=load(sys.argv[1]); vectors=json.load(open(sys.argv[2]))["invalid"]; '
            'assert len(vectors)==53; '
            '\nfor case in vectors:\n'
            ' try: validate(c,parse(case["raw"]))\n'
            ' except Invalid as error: assert str(error)==case["error"]\n'
            ' else: raise AssertionError("accepted_invalid_vector")')
    run([str(python), '-I', '-c', code, str(assets/'examples/contract.json'),
         str(assets/'conformance/conformance-v1.json')], outside, environment)
    commands = [[str(binary), '--unknown', 'SYNTHETIC_ARGUMENT_CANARY'],
                [str(virtual/'bin/mindtunnel-planner'), 'approve', '--ttl', 'SYNTHETIC_ARGUMENT_CANARY'],
                [str(python), '-I', '-m', 'mindtunnel_isolation.linux', '--unknown', 'SYNTHETIC_ARGUMENT_CANARY']]
    for command in commands:
        failed = subprocess.run(command, cwd=outside, env=environment, capture_output=True, timeout=20)
        if failed.returncode != 2 or failed.stdout or failed.stderr != b'Rejected: invalid_arguments\n':
            raise ValueError('installed_argument_error_leak')
    return {'clean_environment':True, 'outside_checkout':True, 'cli_demo_report':True,
            'schemas_installed':len(list((assets/'schemas').glob('*.json'))),
            'invalid_vectors_rejected':len(vectors['invalid']), 'argument_error_privacy':True}


def build_inventory():
    from packaging.requirements import Requirement
    from packaging.utils import canonicalize_name
    queue = ['setuptools', 'wheel']
    found = {}
    while queue:
        name = queue.pop(0)
        key = canonicalize_name(name)
        if key in found:
            continue
        metadata = importlib.metadata.metadata(name)
        requirements = []
        for text in importlib.metadata.requires(name) or []:
            requirement = Requirement(text)
            if requirement.marker is None or requirement.marker.evaluate({'extra':''}):
                requirements.append(text)
                queue.append(requirement.name)
        found[key] = {'name':name, 'version':metadata['Version'], 'role':'build',
                      'requires_python':metadata['Requires-Python'],
                      'license_expression':metadata.get('License-Expression','NOASSERTION'),
                      'active_requirements':requirements}
    return list(found.values())


def verify(artifacts=None):
    uv = shutil.which('uv')
    if not uv:
        raise ValueError('uv_required_offline')
    tools = {name:importlib.metadata.version(name) for name in ('setuptools','wheel')}
    if tools != {'setuptools':'84.2.1','wheel':'0.48.0'}:
        raise ValueError('pinned_build_tools_required')
    environment = {'PATH':os.defpath, 'SOURCE_DATE_EPOCH':EPOCH, 'PYTHONHASHSEED':'0',
                   'UV_PYTHON_DOWNLOADS':'never', 'UV_OFFLINE':'1'}
    with tempfile.TemporaryDirectory() as temporary:
        directory = Path(temporary).resolve()
        source = directory/'source'
        source.mkdir()
        source_bytes = {}
        for name in manifest():
            raw = read_regular(ROOT/name, 16*1024*1024)
            if len(raw) > 16*1024*1024:
                raise ValueError('release_source_limit')
            source_bytes[name] = raw
            target = source/name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            target.chmod(0o644)
            os.utime(target, (int(EPOCH), int(EPOCH)))
        run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'], source, environment)
        run([sys.executable, 'scripts/demo.py'], source, environment)
        wheel, sdist = build(source, directory/'first-build', environment)
        wheel_content = inspect_wheel(wheel, source_bytes)
        sdist_content = inspect_sdist(sdist, source_bytes)
        normalize_sdist(sdist)
        if sdist_content != inspect_sdist(sdist, source_bytes):
            raise ValueError('sdist_normalization_changed_content')
        restored = directory/'restored-source'
        unpack_sdist(sdist, restored)
        run(['bash','bootstrap.sh'], restored, environment)
        second_wheel, second_sdist = build(restored, directory/'second-build', environment)
        if wheel_content != inspect_wheel(second_wheel, source_bytes):
            raise ValueError('wheel_content_not_reproducible')
        if sdist_content != inspect_sdist(second_sdist, source_bytes):
            raise ValueError('sdist_content_not_reproducible')
        normalize_sdist(second_sdist)
        if sdist.read_bytes() != second_sdist.read_bytes():
            raise ValueError('sdist_bytes_not_reproducible')
        wheel_identical = wheel.read_bytes() == second_wheel.read_bytes()
        if not wheel_identical:
            raise ValueError('wheel_bytes_not_reproducible')
        checks = {'wheel':installed_checks(wheel,directory/'wheel-install',uv,environment),
                  'sdist_built_wheel':installed_checks(second_wheel,directory/'sdist-install',uv,environment)}
        if artifacts:
            artifacts = Path(artifacts)
            artifacts.mkdir(mode=0o700)
            shutil.copyfile(wheel, artifacts/wheel.name)
            shutil.copyfile(sdist, artifacts/sdist.name)
        return {'format_version':1, 'python':sys.version.split()[0], 'build_tools':tools, 'build_dependency_inventory':build_inventory(),
                'installer':run([uv,'--version'],directory,environment).decode().strip(),
                'source_date_epoch':int(EPOCH), 'runtime_dependencies':[],
                'source_tests_and_demo':True, 'sdist_source_bootstrap':True, 'clean_installs':checks,
                'wheel_byte_identical':wheel_identical, 'wheel_content_reproducible':True,
                'sdist_content_reproducible':True,
                'sdist_byte_identical':sdist.read_bytes()==second_sdist.read_bytes(),
                'wheel_sha256':digest(wheel.read_bytes()), 'sdist_sha256':digest(sdist.read_bytes()),
                'source_manifest':{name:digest(raw) for name,raw in source_bytes.items()},
                'wheel_members':wheel_content, 'sdist_members':sdist_content,
                'archive_scope':'positive source manifest; every regular archive member inspected; no unknown local files staged'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True)
    parser.add_argument('--artifacts')
    args = parser.parse_args()
    evidence = verify(args.artifacts)
    descriptor = os.open(args.out, os.O_WRONLY|os.O_CREAT|os.O_EXCL, 0o600)
    with os.fdopen(descriptor,'w') as output:
        json.dump(evidence,output,indent=2,sort_keys=True)
        output.write('\n')
    print('Offline release verification passed.')


if __name__ == '__main__':
    main()

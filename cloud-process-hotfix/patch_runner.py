from pathlib import Path

path = Path("/app/cloud_process_runner.py")
source = path.read_text()

download_definition = (
    "def _download_pending_raw(local_base: Path, upload_prefix: str, "
    "max_raw: int) -> list[str]:"
)

helper = '''def _canonical_raw_basename(basename: str) -> str:
    """Map transitional app filenames back to the production CSV contract."""
    if basename.startswith("surface_bursts_"):
        suffix = basename[len("surface_bursts_"):]
        return f"bursts_potholewarrior_{suffix}"

    if basename.startswith("surface_log_"):
        suffix = basename[len("surface_log_"):]
        return f"potholewarrior_{suffix}"

    return basename


def _is_burst_basename(basename: str) -> bool:
    return _canonical_raw_basename(basename).startswith("bursts_")


'''

if source.count(download_definition) != 1:
    raise RuntimeError("Could not locate download function")
source = source.replace(download_definition, helper + download_definition, 1)

old_pending = '''        if basename not in existing_basenames:
            pending.append(uri)'''

new_pending = '''        canonical_basename = _canonical_raw_basename(basename)
        if (
            basename not in existing_basenames
            and canonical_basename not in existing_basenames
        ):
            pending.append(uri)'''

if source.count(old_pending) != 1:
    raise RuntimeError("Could not locate pending-file check")
source = source.replace(old_pending, new_pending, 1)

old_classifier = 'uri.split("/")[-1].startswith("bursts_")'
if source.count(old_classifier) != 2:
    raise RuntimeError("Could not locate both burst classifiers")
source = source.replace(
    old_classifier,
    '_is_burst_basename(uri.split("/")[-1])',
)

old_download = '''    for uri in pending:
        dst = raw_dir / uri.split("/")[-1]
        _run_stream(["gsutil", "cp", uri, str(dst)])
        downloaded.append(str(dst))'''

new_download = '''    for uri in pending:
        upload_basename = uri.split("/")[-1]
        canonical_basename = _canonical_raw_basename(upload_basename)
        dst = raw_dir / canonical_basename

        if canonical_basename != upload_basename:
            print(
                "Normalizing transitional raw filename:",
                upload_basename,
                "→",
                canonical_basename,
            )

        _run_stream(["gsutil", "cp", uri, str(dst)])
        downloaded.append(str(dst))'''

if source.count(old_download) != 1:
    raise RuntimeError("Could not locate raw download loop")
source = source.replace(old_download, new_download, 1)

compile(source, str(path), "exec")
path.write_text(source)

print("Successfully patched:", path)

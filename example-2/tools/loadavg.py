from parser.extractor import extract_file_from_tar


def get_load_avg(filepath: str):
    raw = extract_file_from_tar(filepath, "proc/loadavg")
    return [float(x) for x in raw.split()[:3]] if raw else []
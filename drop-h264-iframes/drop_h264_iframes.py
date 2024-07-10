import subprocess
import argparse
import shutil
import csv
import os
import tempfile
import json
import tqdm


NAL_UNIT_TYPES = {
    0: "Unspecified",
    1: "Coded slice of a non-IDR picture",
    2: "Coded slice data partition A",
    3: "Coded slice data partition B",
    4: "Coded slice data partition C",
    5: "Coded slice of an IDR picture",
    6: "Supplemental enhancement information (SEI)",
    7: "Sequence parameter set",
    8: "Picture parameter set",
    9: "Access unit delimiter",
    10: "End of sequence",
    11: "End of stream",
    12: "Filler data",
    13: "Sequence parameter set extension",
    14: "Prefix NAL unit",
    15: "Subset sequence parameter set",
    16: "Reserved",
    17: "Reserved",
    18: "Reserved",
    19: "Coded slice of an auxiliary coded picture without partitioning",
    20: "Coded slice extension",
    21: "Coded slice extension for depth view components",
    22: "Reserved",
    23: "Reserved",
    24: "Unspecified",
    25: "Unspecified",
    26: "Unspecified",
    27: "Unspecified",
    28: "Unspecified",
    29: "Unspecified",
    30: "Unspecified",
    31: "Unspecified",
}


def setup_directory(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.makedirs(path)


def encode_h264(input_path, output_path, compression_options):
    cmd = [
        "ffmpeg",
        "-loglevel",
        "quiet",
        "-stats",
        "-hide_banner",
        "-i",
        input_path,
        "-an",
        "-vcodec",
        "libx264",
    ]
    for key, value in compression_options.items():
        cmd += [key, value]
    cmd += [
        output_path,
        "-y"
    ]
    subprocess.Popen(cmd).wait()


def probe(input_path, output_path):
    path = os.path.join(output_path, "probe.json")
    output_file = open(path, "w")
    process = subprocess.Popen(
        [
            "ffprobe",
            "-v",
            "quiet",
            "-pretty",
            "-print_format",
            "json",
            "-show_entries",
            "format=size,bit_rate:frame=coded_picture_number,pkt_pts_time,pkt_pts,pkt_dts_time,pkt_dts,pkt_duration_time,pict_type,interlaced_frame,top_field_first,repeat_pict,width,height,sample_aspect_ratio,display_aspect_ratio,r_frame_rate,avg_frame_rate,time_base,pkt_size",
            "-select_streams",
            "v:0",
            input_path
        ],
        stdout=output_file
    )
    process.wait()
    output_file.close()
    with open(path, "r") as file:
        data = json.load(file)
    return data["frames"]


def create_nalu_entry(unit_id, index, probe_result, probe_result_index, offset_start, offset_end, nalu_header):
    forbidden_zero_bit = nalu_header >> 7
    nal_ref_idc = nalu_header >> 5 & 3
    nal_unit_type = nalu_header & 31
    size = offset_end - offset_start
    entry = {
        "id": unit_id,
        "offset_start": offset_start,
        "offset_end": offset_end,
        "size": size,
        "nalu_header": "0x%02X" % nalu_header,
        "forbidden_zero_bit": forbidden_zero_bit,
        "nal_ref_idc": nal_ref_idc,
        "nal_unit_type": nal_unit_type,
        "nal_unit_type_desc": NAL_UNIT_TYPES[nal_unit_type],
    }
    probe_result_index_mod = 0
    if nal_unit_type not in [6, 7, 8]:
        entry.update(probe_result[probe_result_index])
        probe_result_index_mod = 1
    index.append(entry)
    print(f"{unit_id}\t{size}\t{NAL_UNIT_TYPES[nal_unit_type]}")
    return unit_id + 1, probe_result_index + probe_result_index_mod


def split_nalu(input_path, output_path):
    unit_id = 0
    index = []
    offset = 0
    offset_start = 0
    offset_end = None
    nalu_header = None
    buffer = b""
    probe_result = probe(input_path, output_path)
    probe_result_index = 0
    with open(input_path, "rb") as infile:
        while True:
            new_unit = False
            if len(buffer) == 3 and buffer == b'\x00\x00\x01':
                new_unit = True
                offset_end = offset - 3
            elif len(buffer) == 4 and buffer == b'\x00\x00\x00\x01':
                new_unit = True
                offset_end = offset - 4
            elif len(buffer) == 4 and buffer[1:] == b'\x00\x00\x01':
                new_unit = True
                offset_end = offset - 3
            if new_unit:
                if offset_end > offset_start:
                    unit_id, probe_result_index = create_nalu_entry(unit_id, index, probe_result, probe_result_index, offset_start, offset_end, nalu_header)
                offset_start = offset_end
            next_byte = infile.read(1)
            offset += 1
            if new_unit > 0:
                nalu_header = next_byte[0]
            if next_byte == b"":
                create_nalu_entry(unit_id, index, probe_result, probe_result_index, offset_start, offset, nalu_header)
                break
            if len(buffer) < 4:
                buffer = buffer + next_byte
            else:
                buffer = buffer[1:] + next_byte
    with open(os.path.join(output_path, "nalu.csv"), "w", encoding="utf8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=get_fieldnames(index))
        writer.writeheader()
        writer.writerows(index)


def get_fieldnames(items):
    fieldnames = []
    for item in items:
        for key in item:
            if key not in fieldnames:
                fieldnames.append(key)
    return fieldnames


def preprocess(input_path, output_path, compression_options):
    setup_directory(output_path)
    encode_h264(input_path, os.path.join(output_path, "source.h264"), compression_options)
    split_nalu(os.path.join(output_path, "source.h264"), output_path)


def rebuild(input_path, output_path, framerate=30):
    with open(os.path.join(input_path, "nalu.csv"), "r", encoding="utf8", newline="") as file:
        reader = csv.DictReader(file)
        index = list(reader)
    first = True
    with open(os.path.join(input_path, "output.h264"), "wb") as outfile:
        with open(os.path.join(input_path, "source.h264"), "rb") as infile:
            for nalu in tqdm.tqdm(index):
                data = infile.read(int(nalu["size"]))
                if nalu["pict_type"] == "I":
                    if first:
                        first = False
                    else:
                        continue
                outfile.write(data)
    subprocess.Popen(
        [
            "ffmpeg",
            "-loglevel", "quiet",
            "-stats",
            "-hide_banner",
            "-fflags", "+genpts",
            "-r", f"{framerate}",
            "-i", os.path.join(input_path, "output.h264"),
            output_path
        ]
    ).wait()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", type=str, choices=["preprocess", "rebuild", "full", "split", "probe"])
    parser.add_argument("input_path", type=str)
    parser.add_argument("output_path", type=str)
    parser.add_argument("-s", "--sc-threshold", type=int, default=40)
    parser.add_argument("-p", "--profile", type=str, choices=["high", "main", "baseline", "high10", "high422", "high444"], default="main")
    parser.add_argument("-l", "--level", type=float, default=4.0)
    parser.add_argument("-c", "--crf", type=int, default=23)
    parser.add_argument("-g", "--g", type=int, default=250)
    parser.add_argument("-k", "--keyint-min", type=int, default=25)
    parser.add_argument("-b", "--bf", type=int, default=0)
    parser.add_argument("-r", "--framerate", type=float, default=30)
    args = parser.parse_args()
    compression_options = {
        "-crf": str(args.crf),
        "-sc_threshold": str(args.sc_threshold),
        "-profile:v": str(args.profile),
        "-level:v": str(args.level),
        "-g": str(args.g),
        "-keyint_min": str(args.keyint_min),
        "-bf": str(args.bf),
    }
    if args.action == "preprocess":
        preprocess(args.input_path, args.output_path, compression_options)
    elif args.action == "rebuild":
        rebuild(args.input_path, args.output_path, args.framerate)
    elif args.action == "full":
        tempdir = os.path.join(tempfile.gettempdir(), "foo")
        preprocess(args.input_path, tempdir, compression_options)
        rebuild(tempdir, args.output_path, args.framerate)
    elif args.action == "split":
        split_nalu(args.input_path, args.output_path)
    elif args.action == "probe":
        print(probe(args.input_path, args.output_path))


if __name__ == "__main__":
    main()
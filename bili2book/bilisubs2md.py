import argparse
import sys
import re
from pathlib import Path

import srt
from tqdm import tqdm
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_community.chat_models import ChatZhipuAI

COVER_THRES = 0.80
CONTEXT_LEN = 1000
RETRY = 3
ignore_pattern = re.compile(r'["“”‘’。，？！：；、呀啊呃吧呢呐]')


def metric_coverage(subs, text):
    hits = 0
    text = ignore_pattern.sub('', text)
    for sub in subs:
        sub = ignore_pattern.sub('', sub)
        if sub in text:
            hits += 1
    cover_rate = hits / len(subs)
    return cover_rate


def load_chain():
    llm = ChatZhipuAI(model="glm-4-flash")
    system_message = SystemMessagePromptTemplate.from_template(
'''你擅长添加标点符号和分段，要求：
1. 精确保留所有原始内容
2. 适当分段
''')
    human_message = HumanMessagePromptTemplate.from_template(
'''
文件内容：
{user_input}
''', input_variables=["user_input"])
    prompt = ChatPromptTemplate([system_message, human_message])
    chain = prompt | llm
    return chain


def ask_llm(subs, chain, f):
    data = ''.join(subs)

    for _ in range(RETRY):
        response = chain.invoke({"user_input": data})
        text = response.content

        cover_rate = metric_coverage(subs, text)
        if cover_rate < COVER_THRES:
            print(f"[LLM output]: cover_rate {cover_rate:.2f} < {COVER_THRES}, retrying...")
            continue

        f.write(text)
        f.flush()
        return True


def main():
    chain = load_chain()
    parser = argparse.ArgumentParser(description='Convert SRT files to Markdown.')
    parser.add_argument('--srt-dir', type=Path, required=True, help='Directory containing SRT files')
    parser.add_argument('--out-dir', type=Path, help='Directory to output Markdown files (Default: same as SRT directory)')
    args = parser.parse_args()
    srt_dir = args.srt_dir
    out_dir = args.out_dir if args.out_dir else srt_dir

    if not srt_dir.exists():
        raise FileNotFoundError(f"The directory {srt_dir} does not exist.")

    if not srt_dir.is_dir():
        raise NotADirectoryError(f"{srt_dir} is not a directory.")

    if not out_dir.exists():
        out_dir.mkdir(parents=True)

    srt_list = sorted(list(srt_dir.glob("*.srt")))

    for srt_fp in srt_list[:]:
        output_fp = out_dir / srt_fp.name.replace(".srt", ".md")
        data = open(srt_fp).read()
        total_subs = []
        for sub in srt.parse(data):
            total_subs.append(sub.content)

        if output_fp.exists():
            print(f"[Check MD]: {output_fp} exists, checking cover_rate")
            cover_rate = metric_coverage(total_subs, open(output_fp).read())
            if cover_rate > COVER_THRES:
                print(f"[Check MD]: cover_rate {cover_rate:.2f} > {COVER_THRES}, skip")
                continue
            else:
                print(f"[Check MD]: cover_rate {cover_rate:.2f} <= {COVER_THRES}, rerun")

        sub_str_len = 0
        buffer = []
        with open(output_fp, "w") as f:
            for sub in tqdm(total_subs):
                buffer.append(sub)
                sub_str_len += len(sub)
                if sub_str_len >= CONTEXT_LEN:
                    ask_llm(buffer, chain, f)
                    buffer.clear()
                    sub_str_len = 0

            if buffer:
                ask_llm(buffer, chain, f)

    print(f"Finished converting {len(total_subs)} subs. Check markdowns in {out_dir}")

if __name__ == "__main__":
    main()

"""
Copyright 2022-2024 czubix

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import re
import sys

def main(file: str) -> None:
    with open(file, "r") as file:
        content = file.read()

    content = "\n".join(content.splitlines()[len(__doc__.splitlines()) + 1:])

    content = re.sub(r"\n *", r"", content)
    content = re.sub(r" ?(\+|-|\*|/|%|\*\*|//|==|!=|>|>=|<|<=|=|:=|\+=|-=|\*=|/=|%=|//=|\*\*=|,|:) ?", r"\g<1>", content)
    content = re.sub(r"(if|else|for|is|in|not|await) (\(|\[|{|\"|')", r"\g<1>\g<2>", content)
    content = re.sub(r"(\)|]|}|\"|') (if|else|for|is|in|not)", r"\g<1>\g<2>", content)

    content = '"""' + __doc__ + '"""\n\n' + content

    print(content)

if __name__ == "__main__":
    main(sys.argv[1])
import glob
import subprocess
import sys

files = glob.glob('./tweets/*')

for filename in files:
    subprocess.call([sys.executable, 'twtt.py', filename, 'twtts/' + filename.split('/')[-1] + '.twt'])


# def get_all_ascii():
#     some_list = []
#     for filename in files:
#         f = open(filename, 'r');
#         for line in f:
#             new_line = re.sub('&amp;', '&', line)
#             match = re.findall('&[^\s|^&]*?;', new_line)
#             # m = re.match('.*?&lwe;.*', new_line)
#             # if m is not None:
#             #     print filename
#             #     print line
#             if match is not None:
#                 some_list+=(match)

# def get_all_clitics():
#     some_list = []
#     for filename in files:
#         f = open(filename, 'r');
#         for line in f:
#             tweet = remove_anchor_tags(line)
#             tweet = sub_ascii(tweet)
#             match = re.findall('[^\s]\'[^(\s|s)]+', tweet.lower())
#             # m = re.match('.*?&lwe;.*', new_line)
#             # if m is not None:
#             #     print filename
#             #     print line
#             if match is not None:
#                 some_list+=(match)
#     for thing in set(some_list):
#         print thing


# def get_all_html_tags():
#     some_list = []
#     for filename in files:
#         f = open(filename, 'r');
#         for line in f:
#             match = re.findall('<(.).*?>', line)
#             # m = re.match('.*?&lwe;.*', new_line)
#             # if m is not None:
#             #     print filename
#             #     print line
#             some_list += match
#     for thing in set(some_list):
#         print thing
# set(['&lwe;', '&quot;', '&quot</a>;', '&lt;', '&#039;', '&amp;', '&gt;', '&M&quot;'])
# set(['&lwe;', '&quot;', '&quot</a>;', '&lt;', '&#039;', '&amp;', '&gt;'])

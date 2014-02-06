import NLPlib
import re
import sys

# TAGS ADDED TO THE TAGGER:
# MNTN : Mentions
# HASHTG : Hashtags
# EMOT : emoticons
# MULTIPUNC : Multipl Punctuation


emoticon_file = 'Wordlists/__emoticons__'

#punctuation and symbols
punctuation = [',', ';', ':', '~', '@', '#', '$', '%', '^', '&',
               '*', '/', '\\', '|', '-', '+', '_', '=', '(', ')', '[', ']',
               '{', '}', '<', '>', '\'', '"', '.', '!', '?']

# put in this tag where there was a mention.
# adds an extra token which will not be counted when processing tokens.
mention_sub = "__mention__"

# put in this tag where there was a hashtag.
# adds an extra token which will not be counted when processing tokens.
hashtag_sub = "__hashtag__"

number_sub = "__number__"


def remove_anchor_tags(tweet):
    """Remove anchor tags from the tweet.

    Note: The only html tags in these tweets is the anchor tag.
    If anchor tag was a username, then it strips out the tag and removes the
    @ from before the tag
    If anchor tag was a hashtag, it removes the #
    In all other cases, removes the content from the within the tags because
    the content will be a url (with or without the http/www)

    """

    # regex for html anchor tags
    # remove contents if url --> http/www
    anchor_regex = re.compile("<a.*?>(.*?)</a>\.?", re.IGNORECASE)

    # regex for username
    # remove @ symbol.
    anchor_username = re.compile(
                     "@<a.*? class=\".*?(?:username).*?\".*?>(.*?)</a>",
                      re.IGNORECASE)

    # regex for hashtag
    # remove #
    anchor_hashtag = re.compile(
                    "<a.*? class=\".*?(?:hashtag).*?\".*?>#(.*?)</a>",
                    re.IGNORECASE)

    subbed_tweet = re.sub(anchor_username, mention_sub + ' \\1', tweet)
    subbed_tweet = re.sub(anchor_hashtag, hashtag_sub + ' \\1', subbed_tweet)
    subbed_tweet = re.sub(anchor_regex, "", subbed_tweet)

    return subbed_tweet

def sub_ascii(tweet):
    """Replace HTML Char Codes with their ASCII equivalents.

    Specifically replaces the Codes that I found while programatically looking
    through the provided corpus of tweets.
    """

    # Wrote a script to get all the html character codes used. These are them!
    html_to_ascii = {'&quot;' : '"', '&lt;' : '<',
                 '&#039;' : '\'', '&amp;' : '&' , '&gt;' : '>' }

    # do this first because &'s are sometimes escaped leading to things like
    # &amp;lt; istead of &lt;
    subbed_tweet = re.sub('&amp;', '&', tweet)

    for key, value in html_to_ascii.iteritems():
        subbed_tweet = re.sub(key, value, subbed_tweet)

    return subbed_tweet

def tokenize_numbers(tweet):
    """ Replaces all numbers with a single token.

    This captures all numbers including those with , and . in betweet
    """
    return re.sub('(\d+(((,|.)\d+)+)?)', " " + number_sub + " ", tweet).strip()

def break_sentence(tweet):
    """Insert new lines between sentences of a tweet.

    Follows some heuristics for when to and when not to insert the new lines.
     - If there is a quotation mark right after the ending punctuation,
       move the boundary to after the quotation.
     - If the word is immediately precending the ending punctuation is an
       abbrev, then don't split it up here. Note: I do not check for whether
       the abbrev is one that is often used sentence-finally., and I only
       ignore the abbrev if it is followed by a single '.'.
    """

    file_abbrev = open("Wordlists/abbrev.english", "r")
    abbrevs = []
    for abbrev in file_abbrev:
        abbrevs.append(abbrev.lower().strip())
    abbrevs += ['rep.']

    # checks for things like e.g. and p.m.
    abbreviation_regex = re.compile('\s(\w\.(?:\w\.)+)')
    subbed_tweet = re.sub(abbreviation_regex,' \\1 ', tweet)

    demarcating_punctuation = re.compile('([^\s]*?)((?:\.|\?|!)+)(?:"|\')?')

    # This array will have a touple of everything matche, the position of the
    # beginning of punctuation, and where the match ends.
    boundaries = [(m.group(), m.end(1), m.end())
                  for m in
                  re.finditer(demarcating_punctuation, subbed_tweet)]

    abbrev_positions = []
    for m in re.finditer(abbreviation_regex, subbed_tweet):
        abbrev_positions += range(m.start(1), m.end(1)+1)

    pos = 0
    broken_up_tweet = ""
    for boundary in boundaries:
        if not boundary[0].lower() in abbrevs \
        and not boundary[2] in abbrev_positions:
            broken_up_tweet += (subbed_tweet[pos:boundary[1]] +
                " " + subbed_tweet[boundary[1]:boundary[2]]).strip() + "\n"
            pos = boundary[2]
    if pos < len(subbed_tweet):
        broken_up_tweet += subbed_tweet[pos:len(subbed_tweet)].strip()
    return broken_up_tweet.strip()


def tokenize(tweet):
    """Separate the tokens of tweet.
    """

    #punctuation, brackets, quotes, symbols ...
    symbols = [',', ';', '\:', '~', '@', '#', '\$', '%', '\^', '&',
               '\*', '/', '\\', '\|', '-', '\+', '_', '=', '\(', '\)', '\[', '\]',
               '{', '}', '<', '>', '\'', '"']

    others = ['(!|\?)+', '\.\.\.']

    special_symbols = [mention_sub, hashtag_sub, number_sub]


    #clitics
    clitics = ["'s", "'m", "'d", "'ll", "'re", "'ve", "n't"]

    symbs_regex = '(' + '|'.join(symbols) + ')+'

    # joining the clitics first causes the regex to match those first, so "'ve"
    # would be handled as such instead of as "'" and "ve".
    tokenizing_regex = re.compile(
                       '(' + '|'.join(clitics) + '|' +
                       '|'.join(special_symbols) + '|' + '|'.join(others)
                        + '|' + symbs_regex +  ")",
                        re.IGNORECASE)

    # replace all sequences of dashes with a single dash.
    new_tweet = re.sub('-+', '-', tweet)
    new_tweet = re.sub(tokenizing_regex, ' \\1 ', new_tweet)

    return new_tweet

def tag_tweet(tweet):
    """Tag the tokens of the tweet with their POS.
    """

    emoticons = []
    f_emoticons = open(emoticon_file, 'r')
    for emoticon in f_emoticons:
        emoticons.append(emoticon.strip())
    f_emoticons.close()

    tweet_sentences = tweet.split('\n')
    tagged_sentences = ""
    for sent in tweet_sentences:
        tweet_parts = sent.split()
        tags = tagger.tag(tweet_parts)

        count = 0
        for token in tweet_parts:
            if token in emoticons:
                tags[count] = "EMOT"
            # multiple punctuation/symbols is always separated into its own
            # thing. so if any of the chars in the token is punctuation/a symbol
            # then everything is.
            elif token == mention_sub:
                tags[count] = "MNTN"
            elif token == hashtag_sub:
                tags[count] = "HASHTG"
            elif token == number_sub:
                tags[count] = "NUMB"
            elif token[0] in punctuation and tags[count] == "NN":
                tags[count] = "MULTIPUNC"

            count += 1

            # If token is emoticon or multiple punctuation or ! mark or
        tagged_sentences += ' '.join('%s/%s' % t
                            for t in zip(tweet_parts, tags)) + "\n"
    # if tagged_sentences[-1] == "\n" and len(tagged_sentences.strip())>0:
    #     tagged_sentences = tagged_sentences[:-1]
    return tagged_sentences.strip()

def pre_process_tweet(line):
    tweet = remove_anchor_tags(line)
    tweet = sub_ascii(tweet)
    tweet = tokenize_numbers(tweet)
    tweet = break_sentence(tweet)
    tweet = tokenize(tweet)
    tweet = tag_tweet(tweet)
    return tweet

tagger = NLPlib.NLPlib()
if len(sys.argv) != 3:
    print "Incorrect Usage. Format: python twtt.py <input_file> <output_file>"
else:
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    file_i = open(input_file, 'r')
    file_o = open(output_file, 'w')
    for line in file_i:
        tweet = pre_process_tweet(line)
        file_o.write(tweet)
        file_o.write('\n|\n')

#TODO: Tag multiple punctuation things with a different tag instead of NN
#TODO: Close all opened files

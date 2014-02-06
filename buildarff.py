import os
import re
import sys

NUM_TWEETS_PER_FILE = 1000

hashtag_token = "__hashtag__"
mention_token = "__mention__"
number_token = "__number__"

hashtag_tag = "HASHTG"
mention_tag = "MNTN"
number_tag = "NUMB"

class ExtractionAction:
    READ_TOKEN = 1
    READ_TAG = 2
    NONE = 3
    DO_FUTURE_TENSE = 4
    # TBD = 4

relation_name = "twit_classification"

# {Feature_name : (name_of_file_to_read/list of REGEX statemnts
# to match/empty string , FILE ACTION (what to do with file),
# use file?--> If fileaction not None, then read dict instead of file)}
feature_list = {"1person":("First-person", ExtractionAction.READ_TOKEN, True, 0),
                "2person":("Second-person", ExtractionAction.READ_TOKEN, True, 1),
                "3person":("Third-person", ExtractionAction.READ_TOKEN, True, 2),
                "coord_conj":(['CC'], ExtractionAction.READ_TAG, False, 3),
                "past-tense":(['VBD', 'VBN'], ExtractionAction.READ_TAG, False, 4),
                "future-tense":("", ExtractionAction.DO_FUTURE_TENSE, False, 5),
                "commas":([','], ExtractionAction.READ_TAG, False, 6),
                "colons-semicolons":([':',';'], ExtractionAction.READ_TOKEN, False, 7),
                "dashes":(['-'], ExtractionAction.READ_TOKEN, False, 8),
                "paranthesis":(['\)'], ExtractionAction.READ_TAG, False, 9),
                "ellipses":(["\.\.\."], ExtractionAction.READ_TOKEN, False, 10),
                "common-nouns":(["NN", "NNS"], ExtractionAction.READ_TAG, False, 11),
                "proper-nouns":(["NNP", "NNPS"], ExtractionAction.READ_TAG, False, 12),
                "adverbs":(["RB", "RBR", "RBS", "WRB"], ExtractionAction.READ_TAG, False, 13),
                "wh-words":(["WDT", "WP", "WP\$", "WRB"], ExtractionAction.READ_TAG, False, 14),
                "slang":("Slang", ExtractionAction.READ_TOKEN, True, 15),
                "uppercase":("", ExtractionAction.NONE, False, 16),
                "average-len-sent":("", ExtractionAction.NONE, False, 17),
                "average-len-tokens":("", ExtractionAction.NONE, False, 18),
                "number-sentences":("", ExtractionAction.NONE, False, 19),
                # ADDED FEATURES
                "emoticons":(["EMOT"], ExtractionAction.READ_TAG, False, 20),
                "multipleexclaimation":(["(\?|!)+"], ExtractionAction.READ_TOKEN, False, 21),
                "hashtags" : ([hashtag_tag], ExtractionAction.READ_TAG, False, 22),
                "mentions" : ([mention_tag], ExtractionAction.READ_TAG, False, 23),
                #number of numbers in tweet
                "numbers" : ([number_tag], ExtractionAction.READ_TAG, False, 24)
                }

punctuation = [',', ';', ':', '~', '@', '#', '$', '%', '^', '&',
               '*', '/', '\\', '|', '-', '+', '_', '=', '(', ')', '[', ']',
               '{', '}', '<', '>', '\'', '"', '.', '!', '?']

def check_usage(args):
    """Check if the program is being called correctly.
    """

    usage_statement = "Usage: " + args[0] +\
                      "[-<number of tweets>] " +\
                      "[<class-name>:]<filename.twt>[+<filename.twt>...]..." +\
                      " <filename.arff>"
    usage_error = False

    if len(args) < 4:

        if len(args) == 3:

            if args[1][0] == "-":
                usage_error = True

        else:
            usage_error = True

        if usage_error:
            print "Error: Insufficient number of arguments."
            print usage_statement
            return False

    if args[-1][-5:] != '.arff':
        print "Error: Output file format not recognised."
        print usage_statement
        return False

    return True

def write_attribute_definitions_to_file(file, class_name_string):
    """Use the feature_list to write an attribute definition table to the file.
    """
    file.write("@relation " + relation_name + "\n\n")
    for feature, stuff in feature_list.iteritems():
        file.write("@attribute " + feature + " numeric\n")

    file.write("@attribute class " + class_name_string + "\n\n")


def read_file_to_list(filename):
    file = open(filename, 'r')
    ret_list = []

    for line in file:

        if line.strip():
            # print (re.escape(line.strip()))
            ret_list.append(re.escape(line.strip()))

    return ret_list

def process_feature_list():
    """Fixes my construction of the feature list so it doesn't have
    to read from file for every tweet.
    """
    print "Processing Feature List: "

    for feature, value in feature_list.iteritems():
        use_file = value[2];

        if use_file:
            filename = "Wordlists/" + value[0]
            mylist = read_file_to_list(filename)
            feature_list[feature] = (mylist, value[1], False, value[3]);

def get_all_tokens(tweet, remove_mentions_hashtags=False):
    """Split up a tweet into its tokens, getting everything before
    the last '/'.
    """
    all_tokens = tweet.split()
    all_tokens = ['/'.join(pair.split('/')[:-1]) for pair in all_tokens]
    if remove_mentions_hashtags:
        all_tokens = filter(lambda(y):y != mention_token and y!= hashtag_token, all_tokens)
    return all_tokens

def get_all_tags(tweet, remove_mentions_hashtags=False):
    """Split up a tweet into its tags, getting everything after the '/'.
    """
    all_tags = tweet.split()
    all_tags = [pair.split('/')[-1] for pair in all_tags]
    if remove_mentions_hashtags:
        all_tags = filter(lambda(y):y != mention_tag and y != hashtag_tag, all_tags)
    return all_tags

def get_counts_for_token(tweet, feature, mylist):
    """Count the times an element from mylist appears in a token in the tweet.
    """
    # print "Getting count for token for " + feature
    all_tokens = get_all_tokens(tweet)
    count = 0;

    for token in all_tokens:
        for thing in mylist:

            if re.match('^' + thing + '$', token, re.IGNORECASE):
                count+=1

    return count;


def get_counts_for_tags(tweet, feature, mylist):
    """Count the times an element from mylist appears in a tag in the tweet.
    """
    # print "Getting count for tags " + feature
    all_tags = get_all_tags(tweet)
    count = 0;

    for tag in all_tags:
        for thing in mylist:

            if re.match('^' + thing + '$', tag, re.IGNORECASE):
                count+=1

    return count;

def extract_features(tweet):
    """Run through the feature list and extract features from the tweet
    into an ordered list of numbers.
    """

    # print "Extracting features"
    tweet_features = []

    for i in feature_list:
        # append some value for everything in the list to make sure it
        # stays in range.
        tweet_features.append('-1')

    for feature, value in feature_list.iteritems():
        pos = value[3]
        if value[1] == ExtractionAction.READ_TOKEN:
            count = get_counts_for_token(tweet, feature, value[0])
            tweet_features[pos] = str(count)

        elif value[1] == ExtractionAction.READ_TAG:
            count = get_counts_for_tags(tweet, feature, value[0])
            tweet_features[pos] = str(count)

        elif value[1] == ExtractionAction.DO_FUTURE_TENSE:
            count = 0
            pairs = tweet.split()

            for pair in pairs:
                token = '/'.join(pair.split('/')[:-1])
                if re.search("('ll)|(^will$)|(^gonna$)", token, re.IGNORECASE):
                    count += 1
            # doing tweet+" " so that it matches the whitespace at end always
            if re.search("going/VBG\s+to/TO\s+[^s]+/VB\s", tweet+" ", re.IGNORECASE):
                count += 1
            tweet_features[pos] = str(count)

        elif value[1] == ExtractionAction.NONE:

            if feature == "uppercase":
                upper_count = 0
                all_tokens = get_all_tokens(tweet, True)

                for token in all_tokens:
                    if len(token) >= 2 and token.isupper():
                        upper_count+=1

                tweet_features[pos] = str(upper_count)

            elif feature == "average-len-sent":
                num_sents = len(tweet.split("\n"))
                num_tokens = len(get_all_tokens(tweet, True))
                if num_sents == 0:
                    avg = 0
                else:
                    avg = num_tokens/float(num_sents)
                tweet_features[pos] = str(avg)

            elif feature == "average-len-tokens":
                all_tokens = get_all_tokens(tweet, True)
                total_len = 0
                num_tokens = 0

                for token in all_tokens:
                    increment = True

                    for punc in punctuation:
                        if punc in token:
                            increment = False

                    if increment:
                        total_len += len(token)
                        num_tokens += 1

                if num_tokens == 0:
                    avg = 0
                else:
                    avg = total_len/float(num_tokens)
                tweet_features[pos] = str(avg)

            elif feature == "number-sentences":
                tweet_features[pos] = str(len(tweet.split("\n")))

            else:
                #ERROR
                print "Found a ExtractionAction.NONE for feature: " + feature\
                    + " with an undefined action."
        else:
            #ERROR
            print "Extract Features Error. This shouldn't happen"

    return ','.join(tweet_features)


def main():

    args = sys.argv

    # Turning on Debug mode!
    if len(args) == 2 and args[1].lower() == "-debug":
        print "DEBUG MODE ON"
        process_feature_list()
        return

    # Main Variables.
    start = 1
    cap_tweets_at = -1
    file_arff = ""
    # dict of format: {classname:[file1, file2 ...] , ...}
    class_files = {}

    # Return if the input is wrong.
    if not check_usage(args):
        return

    file_arff = open(args[-1], 'w')

    # Parse the input.
    if (args[1][0] == '-'):
        start = 2
        cap_tweets_at = int(args[1][1:])
        if cap_tweets_at > NUM_TWEETS_PER_FILE:
            print "Argument to -n too big. Using " +\
                   NUM_TWEETS_PER_FILE + "instead"

    class_name_string_for_arff = "{"
    for arg in args[start:-1]:
        # if there is something before the semicolon, this gets set to
        # that, if there is no semi colon it gets set correctly anyway
        class_name = arg.split(':')[0]
        class_name_string_for_arff += class_name + ', '
        files_in_class = arg.split(":")[-1].split("+")
        class_files[class_name] = files_in_class
        for filename in files_in_class:
            if not os.path.isfile(filename):
                print "Error: File: " + filename + " does not exist."
                return

    if class_name_string_for_arff[-2:] == ', ':
        class_name_string_for_arff = class_name_string_for_arff[:-2]
    class_name_string_for_arff += "}"

    # Wtite the attribute definition table to the file.
    write_attribute_definitions_to_file(file_arff, class_name_string_for_arff)

    process_feature_list()

    file_arff.write("@data\n")

    for classname, filelist in class_files.iteritems():
        print "Processing Class " + classname

        num_tweets_per_file = cap_tweets_at/len(filelist)
        count = 0

        for filename in filelist:
            count += 1
            if count == len(filelist):
                num_tweets_per_file += cap_tweets_at%len(filelist)
            twttfile = open(filename, 'r')
            num_tweets_read = 0;
            complete_tweet = ""
            for line in twttfile:
                if (line.strip() != "|"):
                    complete_tweet += line + "\n"
                else:
                    # print complete_tweet
                    file_arff.write(extract_features(complete_tweet.strip()) +\
                                    ',' + classname + '\n')
                    complete_tweet = ""
                    num_tweets_read+=1;
                    if num_tweets_per_file >= 0 and num_tweets_read == num_tweets_per_file:
                            break
            # print num_tweets_read

if __name__ == "__main__":
    main()
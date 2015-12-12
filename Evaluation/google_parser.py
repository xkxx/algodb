import json
import os
import wikipedia

def parse_google():
    google_src = "google_search_results"
    google_filtered_data = {}
    filter_outs = ["Category:",
                   "Talk:",
                   "Wikipedia:",
                   "File:",
                   "User:",
                   "File talk:",
                   "Template:",
                   " talk:",
                   "List of ",
                   "(disambiguation)",
                   "(music)",
                   "(film)",
                   "(gaming)",
                   "(company)",
                   "(snack)",
                   "(skiing)",
                   "(novel)",
                   "(album)",
                   "(politics)",
                   "(psychology)",
                   "(social_science)",
                   "(book)",
                   "(pediatrician)"]
    for jsonfile in os.listdir(google_src):
        print(jsonfile)
        with open(os.path.join(google_src, jsonfile), 'r') as jfp:
            jdata = json.load(jfp)
        algo_name = jsonfile.split(".")[0]
        if "items" not in jdata:
            continue

        items = jdata["items"]
        urls = []
        for result in items:
            title = result["title"]

            # Remove improper titles
            should_filter = False
            for remove in filter_outs:
                if title.find(remove) != -1:
                    should_filter = True
            if should_filter:
                continue

            # Remaining links: remove entries where the first sentence does not contain "algorithm"
            wikititle = title[:title.rfind(" - Wikipedia, the free")].strip()
            try:
                page = wikipedia.page(title=wikititle)
            except wikipedia.exceptions.DisambiguationError:
                continue

            first_para = page.content
            if first_para.lower().find("algorithm") == -1:
                continue

            urls.append(result["formattedUrl"])

        google_filtered_data[algo_name] = urls
    return google_filtered_data

def filter_invalid_search(google_data):
    invalid_names = ["Predictive search",
                     "Deep Dense Face Detector",
                     "Zha's algorithm",
                     "Parity Control",
                     "Ephmerides",
                     "Trust search",
                     "Epitome",
                     "Help to diagnosis",
                     "Hungarian",
                     "Woodhouse-Sharp",
                     "Coding scheme that assigns codes to symbols so as to match code lengths with the probabilities of the symbols",
                     "O'Carroll algorithm",
                     "Computation useful in healthcare",
                     "Positions of Moon or other celestial objects"

                     ]
    # Need to change:
    #   Peterson's [+Algorithm]
    #   Banker's [+Algorithm]
    #   Cocktail sort [-(or bidirectional bubble, shaker, ripple, shuttle, happy hour sort)]
    #   Hungarian [+Algorithm]
    #
    # Algorithms not in wikipedia:
    #   Woodhouse-Sharp Algorithm
    #   Zha's algorithm
    #   O'Carroll algorithm
    #   Deep Dense Face Detector
    return google_data

def run():
    google_data = parse_google()
    filtered = filter_invalid_search(google_data)
    with open("google_filtered_results.json", "w") as fp:
        json.dump(filtered, fp, indent=4)

if __name__ == '__main__':
    run()
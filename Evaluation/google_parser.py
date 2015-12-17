import json
import os
import wikipedia
import urllib


def parse_google():
    skip_file = os.listdir("temp")

    json_temp_dirs = "temp"
    if not os.path.exists(json_temp_dirs):
        os.makedirs(json_temp_dirs)

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
        if jsonfile in skip_file:
            continue

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
            formattedURL = result["formattedUrl"]
            page_name = formattedURL[formattedURL.rfind("/")+1:]
            page_name = urllib.unquote(page_name.replace("_", " "))
            try:
                first_para = wikipedia.summary(page_name)
            except wikipedia.exceptions.WikipediaException:
                continue

            if first_para.lower().find("algorithm") == -1:
                continue

            urls.append(formattedURL)
        google_filtered_data[algo_name] = urls
        tempjson = {algo_name: urls}

        with open(os.path.join(json_temp_dirs, jsonfile), "w") as jfp:
            json.dump(tempjson, jfp, indent=4)


def folder_to_file():
    missing_best = {
        "Richardson eigenvector algorithm": "https://en.wikipedia.org/wiki/Modified_Richardson_iteration",
        "DE (Differential evolution)": "https://en.wikipedia.org/wiki/Differential_evolution",
        "Shell sort": "https://en.wikipedia.org/wiki/Shellsort",
        "Line search": "https://en.wikipedia.org/wiki/Line_search",
        "Delta encoding": "https://en.wikipedia.org/wiki/Delta_encoding",
        "Self-organizing map (Kohonen map)": "https://en.wikipedia.org/wiki/Self-organizing_map"
    }

    remove_non_algos = [
        "Ant colony optimization",          # Vague
        "Branch and bound",                 # Vague
        "Ant-algorithms",                   # Dup entry
        "Coloring algorithm",               # Vague
        "Divide-and-conquer",               # Vague
        "Selection algorithm",              # Vague
        "Page replacement",                 # Vague
        "Splay tree",                       # Data structure not algorithm
        "Fourier transform multiplication"  # Ground truth doesn't have correct links
    ]

    jdata = {}
    for jsonFile in os.listdir("temp"):
        with open(os.path.join("temp", jsonFile)) as fp:
            single = json.load(fp)
        for k, v in single.items():
            if len(v) >= 5 and k not in remove_non_algos:
                res = []
                if k in missing_best:
                    res.append(missing_best[k])
                for url in v:
                    if "..." in url:
                        res.append(url.replace("...", "wiki").replace(" ", ""))
                    else:
                        res.append(url)
                jdata[k] = res
    return jdata


def run():
    parse_google()
    google_data = folder_to_file()
    print(len(google_data))
    with open("google_filtered_results.json", "w") as fp:
        json.dump(google_data, fp, indent=4)
if __name__ == '__main__':
    run()

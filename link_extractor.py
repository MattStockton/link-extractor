#!/usr/bin/env python
import sys, argparse, os, re
from collections import OrderedDict
from BeautifulSoup import BeautifulSoup
import requests

def main(args):
    """
    Command line tool to extract links from web pages
    """
    parser = argparse.ArgumentParser(description="Command line tool to extract links from web pages")
    parser.add_argument("-i", "--input-file", help="Location of csv file containing pages to scrape, and what to scrape for (see sample_input.csv for format)", required=True)
    parser.add_argument("-o", "--output-dir", help="Location of output directory where results.csv should be written", required=True)
   
    parsed_args = parser.parse_args(args=args)
    cmd_vars = vars(parsed_args)
    
    output_dir = cmd_vars["output_dir"]
    
    if not os.path.isdir(output_dir):
        print "Output directory should exist before running this script"
        sys.exit()
        
    output_file = os.path.join(output_dir,"results.csv")
            
    try:
        input_lines = [line.strip().split(",") for line in open(cmd_vars["input_file"])]
        source_urls = [line[0] for line in input_lines[1:] if line[0]]
        look_for_urls = [line[1] for line in input_lines[1:] if len(line) > 1 and line[1]]
    except IOError:
        print "There was a problem opening the input file"
        sys.exit()
    
    source_urls_to_results = OrderedDict()
    for source_url in source_urls:        
        try:
            r = requests.get("http://{0}?".format(source_url), allow_redirects=True)
            source_urls_to_results[source_url] = OrderedDict()
        except requests.exceptions.ConnectionError:
            print "Connection error for {0}, skipping".format(source_url)
            continue
        
        soup = BeautifulSoup(r.text)
        for look_for_url in look_for_urls:
            matches = soup.findAll("a", href=re.compile(look_for_url))
            # Do some basic deduplication of links that are found
            source_urls_to_results[source_url][look_for_url] = \
                set([match["href"].lower().replace("https://","").replace("http://","").replace("www.","") for match in matches])
            
    print source_urls_to_results
    
    with open(output_file, "w") as out_file:
        out_file.write("urls," + ", ".join(look_for_urls) + "\n")
        for source_url in source_urls_to_results.keys():
            out_file.write(source_url + ",")
            for cur_url_set in source_urls_to_results[source_url].values():
                # Wrap cell results in '' so that we can easily import into Excel
                out_file.write("'" + ",".join(cur_url_set) + "',")
            out_file.write("\n")
    
if __name__ == "__main__":
    main(sys.argv[1:])
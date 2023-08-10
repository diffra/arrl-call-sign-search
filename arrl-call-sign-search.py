#!/usr/bin/env python3

import argparse
import lxml.html
import re
import requests
import sys
import tabulate
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError


def build_query_payload(callsign: str) -> dict:
    query_payload = {}
    query_payload["_method"] = "POST"
    query_payload["data[Search][terms]"] = callsign

    return query_payload

def get_lat_long(address):
    try:
        geolocator = Nominatim(user_agent="arrl_call-sign_search")
        location = geolocator.geocode(query=address, timeout=2)
        
        if location:
            return location.latitude, location.longitude
        else:
            return None, None

    except GeocoderTimedOut:
        print("Error: The geocoding service timed out.")
        return None, None

    except GeocoderServiceError as e:
        print("Error: An error occurred with the geocoding service.")
        print(e)
        return None, None

    except Exception as e:
        print(f"Unexpected error: {e}")
        return None, None

def find_maidenhead(address):
    latitude, longitude = get_lat_long(address)
    
    # Ensure the longitude is in the range [-180, 180]
    longitude += 180
    latitude += 90

    # Calculate the locator characters
    first_field = chr(int(longitude // 20) + ord('A'))
    second_field = chr(int(latitude // 10) + ord('A'))
    first_square = str(int((longitude % 20) // 2))
    second_square = str(int(latitude % 10))
    third_subsquare = chr(int((longitude % 2) * 12) + ord('a'))
    fourth_subsquare = chr(int((latitude % 1) * 24) + ord('a'))

    # Concatenate the characters to form the Maidenhead locator
    maidenhead_locator = first_field + second_field + first_square + second_square + third_subsquare + fourth_subsquare

    return maidenhead_locator

if __name__ == "__main__":
    # set up command arguments
    parser = argparse.ArgumentParser(
        description="Ham Radio Call Sign Search Utility - ARRL"
    )
    parser.add_argument(
        "--pretty", required=False, action="store_true", help="print pretty format"
    )
    parser.add_argument("callsign", type=str, help="ham radio call sign string")
    args = parser.parse_args()

    # set up constants
    arrl_call_sign_search_url = "https://www.arrl.org/advanced-call-sign-search"
    output = {}

    # build query payload
    payload = build_query_payload(args.callsign)

    # send HTTP request and process the response
    try:
        response = requests.post(arrl_call_sign_search_url, data=payload)
    except Exception as e:
        print(f"ERROR: Could not send HTTP request to ARRL URL: {e}", file=sys.stderr)
        sys.exit(2)

    if response.status_code != 200:
        print(
            "ERROR: Non-200 HTTP response code retrieved from ARRL URL", file=sys.stderr
        )
        sys.exit(3)

    response_xml = lxml.html.fromstring(response.text)
    try:
        title = response_xml.xpath("//div[@class='list2']/ul/li/h3/text()")[0]
        call_sign_details_response = response_xml.xpath(
            "//div[@class='list2']/ul/li/p/text()"
        )

        # some results do not have <p> tag
        if not call_sign_details_response:
            call_sign_details_response = response_xml.xpath(
                "//div[@class='list2']/ul/li/text()"
            )
    except Exception:
        print(f"ERROR: Could not get proper response from ARRL URL", file=sys.stderr)
        sys.exit(4)

    # generate output
    output["title"] = re.sub(r"\t+", "", title.strip())
    output["basic_info"] = []
    output["tables"] = []

    for item in call_sign_details_response:
        if not re.match(r"^\s+$", item):
            line = re.sub(r"\t+", "", item).strip()
            if re.match(r".*:\s+.*", line):
                key, value = line.split(":")
                output["tables"].append([key, value.strip()])
            else:
                output["basic_info"].append(line)
    
    #Look up maidenhead 
    try:
        address = call_sign_details_response[1].strip()
        output["tables"].append(["Grid square", find_maidenhead(address)])
    except Exception as e: 
        print(e)

    print(output["title"])
    for item in output["basic_info"]:
        print(item)

    if args.pretty:
        table_format = "simple_grid"
        print(tabulate.tabulate(output["tables"], tablefmt=table_format))
    else:
        for item in output["tables"]:
            print(f"{item[0]}: {item[1]}")

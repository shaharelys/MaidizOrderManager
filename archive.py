
def clean_address(address):
    # TODO: fix this to work with this "רח׳ אורה 5, רמת גן, ישראל קומה 7 דירה 20 , רמת גן"
    # Regular expression pattern to find relevant address parts
    pattern = re.compile(r"([\w\d\s'-]+(?:\s[\w\d'-]+)?)(?:\s\d+)(?:\s[\w\d\s'-]+)")

    # Search for a match in the input string
    match = pattern.search(address)

    # If a match is found, return the cleaned address, else return the original string
    if match:
        return match.group().strip()
    else:
        return address


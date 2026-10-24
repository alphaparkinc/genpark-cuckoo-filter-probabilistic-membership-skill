"""Example usage for GenPark Cuckoo Filter.
100% Python Standard Library.
"""

from client import CuckooFilter

def main():
    filter_set = CuckooFilter(capacity=500)
    
    # Store blocked domains or toxic keywords
    blocked_terms = ["malware.test", "phishing.test", "toxic_payload_sample"]
    for term in blocked_terms:
        filter_set.insert(term)
        
    print("Contains 'malware.test':", filter_set.contains("malware.test"))
    print("Contains 'clean_domain.com':", filter_set.contains("clean_domain.com"))
    
    # Dynamic deletion support (unlike standard Bloom filter)
    filter_set.delete("malware.test")
    print("After delete 'malware.test':", filter_set.contains("malware.test"))
    print("Stats:", filter_set.get_stats())

if __name__ == "__main__":
    main()

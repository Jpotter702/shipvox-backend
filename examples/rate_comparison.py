# Example usage
comparer = RateComparer()
result = comparer.compare_rates(fedex_rates, ups_rates)

print(f"Cheapest Option: {result.cheapest_option.carrier} {result.cheapest_option.service_name}")
print(f"Price: ${result.cheapest_option.total_charge:.2f}")

print(f"\nFastest Reasonable Option: {result.fastest_reasonable_option.carrier} "
      f"{result.fastest_reasonable_option.service_name}")
print(f"Price: ${result.fastest_reasonable_option.total_charge:.2f}")
print(f"Transit Days: {result.fastest_reasonable_option.transit_days}")
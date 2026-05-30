import time
import requests
import statistics
import math
import random
import pandas as pd

class LatencyBenchmark:

    def __init__(self):

        self.BASE_URL = "http://127.0.0.1:5000/api/"

        self.N_REQUESTS = 100
        self.TEAMS = (
            pd.read_csv("../csv/team_data.csv")["Team"]
            .dropna()
            .unique()
            .tolist()
        )


    def makeRequests(self, endpoint):
        latencies = []
        URL = self.BASE_URL + endpoint

        for i in range(self.N_REQUESTS):
            start = time.perf_counter()
            r = requests.get(URL)
            r.raise_for_status()
            latencies.append(time.perf_counter() - start)

        latencies.sort()

        return latencies
    
    def percentile(self, data, p):
        idx = int(len(data) * p)
        return data[min(idx, len(data) - 1)]
    
    def printResults(self, data):
        print(f"avg: {statistics.mean(data) * 1000:.2f} ms")
        print(f"p50: {self.percentile(data, 0.50) * 1000:.2f} ms")
        print(f"p95: {self.percentile(data, 0.95) * 1000:.2f} ms")
        print(f"p99: {self.percentile(data, 0.99) * 1000:.2f} ms")

    def benchmarkGetTeamRequest(self):
        t1 = random.choice(self.TEAMS)
        latencies = self.makeRequests(f"info/{t1}")
        self.printResults(latencies)

    def benchmarkGetTeamsData(self):
        t1 = random.choice(self.TEAMS)
        t2 = random.choice(self.TEAMS)
        latencies = self.makeRequests(f"matchup_data/{t1}/{t2}")
        self.printResults(latencies)

    def benchmarkPredict(self):
        t1 = random.choice(self.TEAMS)
        t2 = random.choice(self.TEAMS)
        latencies = self.makeRequests(f"predict/{t1}/{t2}")
        self.printResults(latencies)


if __name__ == "__main__":
    benchmark = LatencyBenchmark()

    print("Benchmarking Get Team Request:")
    benchmark.benchmarkGetTeamRequest()
    print("\nBenchmarking Get Teams Data Request:")
    benchmark.benchmarkGetTeamsData()
    print("\nBenchmarking Predict Request:")
    benchmark.benchmarkPredict()



## Performance

Latency was measured locally using repeated HTTP requests. 
Measurements taken over 100 requests on localhost.
January 19th:



| Endpoint | Avg | p95 | p 99 |
|--------|-----|-----|
| GET /api/info/<team> | 22 ms | 42 ms | 79 ms|
| GET /api/matchup_data | 23 ms | 23 ms | 26 ms |
| GET /api/predict | 44 ms | 52 ms | 71 ms |



Jan 23: Added a global predictor object resulting in an 80% latency reduction.

| Endpoint | Avg | p95 | p 99 |
|--------|-----|-----|
| GET /api/info/<team> | 2.9 ms | 5.2 ms | 7.8 ms|
| GET /api/matchup_data | 5.7 ms | 7.6 ms | 8.6 ms |
| GET /api/predict | 8.9 ms | 9.5 ms | 10 ms |

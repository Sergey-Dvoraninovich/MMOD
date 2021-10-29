from plots import build_diff_plot, build_stationarity_plot, build_stationarity_diff_plot
from smo_utils import run_model, get_time_in_smo, get_empirical_p, get_requests_in_smo, get_time_in_line, get_requests_in_query, get_decline_probability, get_requests_in_processing, get_stationarity_data, generate_requests, calculate_theoretical_data, count_xi_diffs

n = 5
m = 4
lambda_val = 2
mu = 0.5
v = 0.5
work_time = 900

state_log, requests = run_model(n, m, lambda_val, mu, v, work_time)

work_times = [3600, 360, 60]
stationarity_data = get_stationarity_data(n, m, lambda_val, mu, v, work_times)

theoretical_p, A, p_decline, L_line, L_smo, T_line, T_smo, n_processing = calculate_theoretical_data(n, m, lambda_val, mu, v)
print("\nTheoretical probabilities")
print("   in processing: " + str(theoretical_p[:n + 1]))
print("         in line: " + str(theoretical_p[n + 1:]))
print("Theoretical decline probability")
print(p_decline)
print("Theoretical requests in line")
print(L_line)
print("Theoretical requests in SMO")
print(L_smo)
print("Theoretical requests in processing")
print(n_processing)
print("Theoretical time in line")
print(T_line)
print("Theoretical time in SMO")
print(T_smo)

empirical_p = get_empirical_p(state_log, n, m)
print("\nTheoretical probabilities")
print("   in processing: " + str(empirical_p[:n + 1]))
print("         in line: " + str(empirical_p[n + 1:]))
empirical_p_decline = get_decline_probability(requests, n, m)
print("Empirical decline probability")
print(empirical_p_decline)
empirical_L_line = get_requests_in_query(empirical_p, n, m)
print("Empirical requests in line")
print(empirical_L_line)
empirical_L_smo = get_requests_in_smo(empirical_p, n, m)
print("Empirical requests in smo")
print(empirical_L_smo)
empirical_n_processing = get_requests_in_processing(empirical_p, n, m)
print("Empirical requests in processing")
print(empirical_n_processing)
empirical_T_line = get_time_in_line(empirical_L_line, lambda_val)
print("Empirical time in line")
print(empirical_T_line)
empirical_T_smo = get_time_in_smo(requests, n, m)
print("Empirical time in SMO")
print(empirical_T_smo)

build_diff_plot(theoretical_p, empirical_p, n, m)
colors = ['#873e44', '#ab5c68', '#cc9293']
build_stationarity_plot(stationarity_data, work_times, colors, n, m)

# work_times = [3600, 900, 700, 500, 400, 300]
# stationarity_data = get_stationarity_data(n, m, lambda_val, mu, v, work_times)
# differences = count_xi_diffs(stationarity_data, n, m, lambda_val, work_time)
# build_stationarity_diff_plot(differences, work_times, n, m)


from . import download_data, analysis
from .vis import compose_graphs_plot_folium
from .utils.authority_names import reverse_search

def batch_prow_analyse_authorities(authorities, fn_data_prefix="data", fn_out_prefix="output"):
    for authority, region in authorities:

        authority_code = reverse_search(authority.split(", ")[0])

        fn_row    = f"{fn_data_prefix}/row/{authority_code}"
        fn_public = f"{fn_data_prefix}/public/{region}"
        fn_graph  = f"{fn_data_prefix}/osmnx/{authority_code}"
        fn_out    = f"{fn_out_prefix}/{authority_code}"

        print(f"Analysis for authority '{authority}' code '{authority_code}' in region '{region}'. Output to {fn_out}")

        if analysis.check_analysis_exists(fn_out):
            continue

        print("1. Download RoW data")
        download_data.download_row_data(authority_code, fn=fn_row)

        print("2. Download public GPS data")
        download_data.download_public_gps_data(region, fn=fn_public)

        print("3. Get graph boundaries")
        graph_boundary = download_data.get_graph_boundary(authority)

        print("4. Download graphs")
        download_data.download_graphs(graph_boundary, fn=fn_graph)

        print("5. Perform analysis")
        analysis.analyse_batch(row_data=fn_row, public_data=fn_public, graph_data=fn_graph, graph_boundary=graph_boundary, out_fn=fn_out)
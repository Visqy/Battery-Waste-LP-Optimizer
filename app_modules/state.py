from shiny import reactive
from battery_optimizer.default_data import load_default_data


def create_state():
    cc, rf, tc = load_default_data()

    class State:
        data_source = reactive.Value("default")
        collection_centers = reactive.Value(cc)
        recycling_facilities = reactive.Value(rf)
        transport_costs = reactive.Value(tc)
        validation_result = reactive.Value(None)
        optimization_result = reactive.Value(None)
        processed_results = reactive.Value(None)
        messages = reactive.Value([])

    return State()
import googlemaps
from sklearn.cluster import KMeans
from config import MAPS_API_KEY
from CONSTS import HOME_BASE
import numpy as np
import requests
from urllib.parse import urlencode
from urllib.parse import quote
import requests
import googlemaps
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


def get_coordinates_from_address(address, api_key):
    gmaps = googlemaps.Client(key=api_key)
    geocode_result = gmaps.geocode(address)
    print(f"Geocode API response: {geocode_result}")  # Add this line to print the response
    if geocode_result and 'geometry' in geocode_result[0]:
        lat = geocode_result[0]['geometry']['location']['lat']
        lng = geocode_result[0]['geometry']['location']['lng']
        return lat, lng
    return None


def get_order_coordinates(customers_dict, upcoming_orders):
    orders_coordinates = []
    for order in upcoming_orders:
        customer_phone = order['customer_phone']
        coordinates = customers_dict[customer_phone]['coordinates']
        orders_coordinates.append(coordinates)
    return orders_coordinates


def cluster_orders(orders_coordinates, number_of_delivery_persons):
    kmeans = KMeans(n_clusters=number_of_delivery_persons, random_state=0)
    kmeans.fit(orders_coordinates)
    labels = kmeans.labels_
    return labels


def get_route_links(orders_coordinates, labels, number_of_delivery_persons):
    gmaps = googlemaps.Client(key=MAPS_API_KEY)

    # Add TSP optimization function
    def create_data_model(coordinates_list):
        data = {}
        data['distance_matrix'] = create_distance_matrix(coordinates_list, gmaps)
        data['num_vehicles'] = 1
        data['depot'] = 0
        return data

    def print_solution(manager, routing, solution):
        index = routing.Start(0)
        plan_output = []
        while not routing.IsEnd(index):
            plan_output.append(manager.IndexToNode(index))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
        plan_output.append(manager.IndexToNode(index))
        return plan_output

    def optimize_tsp(data):
        manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                               data['num_vehicles'], data['depot'])

        routing = pywrapcp.RoutingModel(manager)

        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            # TODO: maybe change [airial] distance to driving time distance
            return data['distance_matrix'][from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)

        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

        solution = routing.SolveWithParameters(search_parameters)

        if solution:
            return print_solution(manager, routing, solution)
        else:
            return None

    def create_distance_matrix(locations, gmaps_client):
        distance_matrix = []
        for origin in locations:
            row = []
            for destination in locations:
                if origin == destination:
                    row.append(0)
                else:
                    row.append(gmaps_client.distance_matrix(origins=[origin],
                                                            destinations=[destination],
                                                            mode="driving",
                                                            units="metric")['rows'][0]['elements'][0]['distance']['value'])
            distance_matrix.append(row)
        return distance_matrix

    routes_links = []

    for i in range(number_of_delivery_persons):
        cluster_points = [coord for coord, label in zip(orders_coordinates, labels) if label == i]
        data = create_data_model(cluster_points)
        tsp_route = optimize_tsp(data)[:-1]

        if tsp_route:
            route_links = [(cluster_points[tsp_route[i]], cluster_points[tsp_route[i + 1]]) for i in range(len(tsp_route) - 1)]
            routes_links.append(route_links)

    return routes_links


def generate_google_maps_link(home_base_coordinates, waypoints, mode='bicycling'):
    origin = f"{home_base_coordinates[0]},{home_base_coordinates[1]}"
    destination = f"{waypoints[-1][-1][0]},{waypoints[-1][-1][1]}"
    waypoints_str = '|'.join([f"{point[0][0]},{point[0][1]}" for point in waypoints])

    return f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}&waypoints={waypoints_str}&travelmode={mode}"


def manage_trip(number_of_delivery_persons, customers_dict, upcoming_orders):
    home_base = HOME_BASE
    print(f"Home base address: {home_base}")
    gmaps = googlemaps.Client(key=MAPS_API_KEY)
    home_base_coordinates = get_coordinates_from_address(home_base, MAPS_API_KEY)
    print(f"Home base coordinates: {home_base_coordinates}")

    orders_coordinates = get_order_coordinates(customers_dict, upcoming_orders)
    labels = cluster_orders(orders_coordinates, number_of_delivery_persons)
    routes_coordinates = get_route_links(orders_coordinates, labels, number_of_delivery_persons)

    routes_links = [generate_google_maps_link(home_base_coordinates, route, mode='bicycling') for route in routes_coordinates]

    return routes_links


if __name__ == "__main__":
    print("Testing...")
    # Mock data for testing
    customers_dict = {
        "123456789": {"name": "John Doe", "address": "Katznelson St 3, Givatayim",
                      "coordinates": (32.073470, 34.811949)},
        "987654321": {"name": "Jane Smith", "address": "Shderot Yerushalayim 15, Ramat Gan",
                      "coordinates": (32.067566, 34.811123)},
        "555555555": {"name": "Alice Brown", "address": "Aluf David St 9, Givatayim",
                      "coordinates": (32.073163, 34.808260)},
        "111111111": {"name": "Bob Green", "address": "HaShlosha St 15, Ramat Gan",
                      "coordinates": (32.077587, 34.810444)},
        "222222222": {"name": "Charlie Black", "address": "Gordon St 22, Ramat Gan",
                      "coordinates": (32.072889, 34.814575)},
        "333333333": {"name": "David White", "address": "Weizmann St 12, Givatayim",
                      "coordinates": (32.069623, 34.807528)},
        "444444444": {"name": "Emma Blue", "address": "Bialik St 8, Ramat Gan",
                      "coordinates": (32.082873, 34.816640)},
        "666666666": {"name": "Fiona Red", "address": "Ben Gurion St 18, Givatayim",
                      "coordinates": (32.078096, 34.812647)},
        "777777777": {"name": "George Gray", "address": "Aminadav St 5, Ramat Gan",
                      "coordinates": (32.066710, 34.814808)},
        "888888888": {"name": "Hannah Yellow", "address": "HaRoe St 2, Givatayim",
                      "coordinates": (32.083276, 34.822222)},
        "999999999": {"name": "Ian Orange", "address": "Korazin St 10, Ramat Gan",
                      "coordinates": (32.082376, 34.815649)},
        "000000000": {"name": "Julia Purple", "address": "Arlozorov St 3, Givatayim",
                      "coordinates": (32.074971, 34.812486)},
    }

    upcoming_orders = [
        {"customer_phone": "123456789"},
        {"customer_phone": "987654321"},
        {"customer_phone": "555555555"},
        {"customer_phone": "111111111"},
        {"customer_phone": "222222222"},
        {"customer_phone": "333333333"},
        {"customer_phone": "444444444"},
        {"customer_phone": "666666666"},
        {"customer_phone": "777777777"},
        {"customer_phone": "888888888"},
        {"customer_phone": "999999999"},
        {"customer_phone": "000000000"},
    ]

    # Test the manage_trip function
    number_of_delivery_persons = 2
    routes_links = manage_trip(number_of_delivery_persons, customers_dict, upcoming_orders)
    print("Google Maps URLs:")
    for i, url in enumerate(routes_links, start=1):
        print(f"Route {i}: {url}")



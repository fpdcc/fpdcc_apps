from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import geopandas as gpd
import geojson as gj

_transport = RequestsHTTPTransport(
    url='http://localhost:8080/v1alpha1/graphql/',
    use_json=True,
)


client = Client(
    transport=_transport,
    fetch_schema_from_transport=True,
)
query = gql("""
{
  quercus_poi_info (where: {namesBynameid: {name: {_like:"%Dan Ryan%"}}})
  {
    poi_info_id
    names: namesBynameid{
      name
    }
    pointsofinterest: pointsofinterestBypointsofinterestId {
      geom
    }
  }
}
""")

print(client.execute(query))

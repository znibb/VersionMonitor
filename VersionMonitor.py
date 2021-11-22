from flask import Flask
from flask_restful import Resource, Api, reqparse
import pandas as pd

app = Flask(__name__)
api = Api(app)

class Version(Resource):
    def get(self):
        # Create parser
        parser = reqparse.RequestParser()

        # Specift parser arguments
        parser.add_argument('name', required=True)

        # Parse arguments
        args = parser.parse_args()

        # Read csv file
        data = pd.read_csv('data.csv')

        # If entry exists, return it
        if args['name'] in list(data['name']):
            # return {'data': f"'{data.loc[data['version']]}'"}, 200
            return {'data': f"'{data.loc[data['name'] == args['name'], ['version']].values[0][0]}'"}, 200

        # Else return error
        else:
            return {'message': f"'{args['name']}' not found."}, 404

        # data = data.to_dict()
        # return {'data': data}, 200

    def post(self):
        # Create parser
        parser = reqparse.RequestParser()

        # Specify parser arguments
        parser.add_argument('name', required=True)
        parser.add_argument('version', required=True)
        parser.add_argument('updated', required=True)

        # Parse arguments
        args = parser.parse_args()

        # Read csv file
        data = pd.read_csv('data.csv')

        # If entry already exists, return error
        if args['name'] in list(data['name']):
            return {'message': f"'{args['name']}' already exists."}, 401

        # Else add entry
        else:
            data_dict = {
                'name': args['name'],
                'version': args['version'],
                'updated': args['updated']
            }
            new_data = pd.DataFrame([data_dict])

            data = data.append(new_data, ignore_index=True)
            data.to_csv('data.csv', index=False)

            return {'data': data.to_dict()}, 200

    def put(self):
        # Create parser
        parser = reqparse.RequestParser()

        # Specify parser arguments
        parser.add_argument('name', required=True)
        parser.add_argument('version', required=True)
        parser.add_argument('updated', required=True)

        # Parse arguments
        args = parser.parse_args()

        # Read csv file
        data = pd.read_csv('data.csv')

        # If name exists, update values
        if args['name'] in list(data['name']):
            data.loc[data['name'] == args['name'], ['version']] = args['version']
            data.loc[data['name'] == args['name'], ['updated']] = args['updated']

            data.to_csv('data.csv', index=False)

            return {'data': data.to_dict()}, 200

        # Else return error
        else:
            return {'message': f"'{args['name']}' not found."}, 404

    def delete(self):
        # Create parser
        parser = reqparse.RequestParser()

        # Specify parser arguments
        parser.add_argument('name', required=True)

        # Parse arguments
        args = parser.parse_args()

        # Read csv file
        data = pd.read_csv('data.csv')

        # If name exists, delete the entry
        if args['name'] in list(data['name']):
            # Keep all data where the name doesn't match
            data = data[data['name'] != args['name']]

            # Save back to csv
            data.to_csv('data.csv', index=False)

            # Return
            return {'data': data.to_dict()}, 200
        
        # Else return error
        else:
            return {'message': f"'{args['name']}' not found."}, 404

api.add_resource(Version, '/version')

if __name__ == '__main__':
    app.run()
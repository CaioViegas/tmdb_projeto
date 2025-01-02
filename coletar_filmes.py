import requests
import json  
import csv   
import os

def puxar_id_genero(api_key, genre_name="Animation"):
    url_genres = f'https://api.themoviedb.org/3/genre/movie/list?api_key={api_key}&language=en-US'
    response = requests.get(url_genres)
    genres = response.json()
    for genre in genres['genres']:
        if genre['name'] == genre_name:
            return genre['id']
    return None

def filmes_por_genero(api_key, genre_id, pages=5):
    todos_filmes = []
    for page in range(1, pages + 1):
        url_movies = f'https://api.themoviedb.org/3/discover/movie?api_key={api_key}&language=en-US&with_genres={genre_id}&sort_by=popularity.desc&page={page}'
        response = requests.get(url_movies)
        data = response.json()
        todos_filmes.extend(data.get('results', []))
    return todos_filmes

def enriquecer_dados_filmes(api_key, movies):
    lista_filmes_enriquecidos = []
    for movie in movies:  # Processar todos os filmes
        movie_id = movie['id']
        
        url_details = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US'
        response_details = requests.get(url_details)
        detailed_data = response_details.json()
        
        url_credits = f'https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={api_key}&language=en-US'
        response_credits = requests.get(url_credits)
        credits_data = response_credits.json()
        
        director = next(
            (crew_member['name'] for crew_member in credits_data.get('crew', []) if crew_member['job'] == "Director"),
            None  
        )
        
        movie.update({
            'budget': detailed_data.get('budget'),
            'revenue': detailed_data.get('revenue'),
            'runtime': detailed_data.get('runtime'),
            'tagline': detailed_data.get('tagline'),
            'release_date': detailed_data.get('release_date'),
            'director': director,
        })
        lista_filmes_enriquecidos.append(movie)
    return lista_filmes_enriquecidos

def salvar_json(data, directory, filename="movies.json"):
    os.makedirs(directory, exist_ok=True)  
    filepath = os.path.join(directory, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Arquivo JSON salvo em: {filepath}")

# Função para salvar os dados em CSV
def salvar_csv(data, directory, filename="movies.csv"):
    os.makedirs(directory, exist_ok=True)  
    filepath = os.path.join(directory, filename)
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print(f"Arquivo CSV salvo em: {filepath}")

if __name__ == "__main__":

    API_KEY = input("Insira a chave da API: ")

    diretorio_data = os.path.join(os.getcwd(), "Data")

    # Obter o ID do gênero "Animation"
    id_genero = puxar_id_genero(API_KEY, "Animation")
    print(f"ID do gênero 'Animation': {id_genero}")

    # Coletar filmes
    filmes = filmes_por_genero(API_KEY, id_genero, pages=10)
    print(f"Total de filmes coletados: {len(filmes)}")

    # Enriquecer dados
    filmes_enriquecidos = enriquecer_dados_filmes(API_KEY, filmes)
    print(f"Filmes enriquecidos: {len(filmes_enriquecidos)}")

    # Salvar dados em diferentes formatos
    salvar_json(filmes_enriquecidos, diretorio_data, "filmes_animacao.json")
    salvar_csv(filmes_enriquecidos, diretorio_data, "filmes_animacao.csv")
    print("Dados salvos com sucesso!")
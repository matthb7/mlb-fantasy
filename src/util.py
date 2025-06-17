PLAYER_NAME_MAPPING = {
    'A Rutschman': 'Adley Rutschman',
    'V Guerrero Jr': 'Vladimir Guerrero',
    'S Horwitz': 'Spencer Horwitz',
    'E Suarez': 'Eugenio Suárez',
    'G Perdomo': 'Geraldo Perdomo',
    'C Bellinger': 'Cody Bellinger',
    'T Soderstrom': 'Tyler Soderstrom',
    'M Trout': 'Mike Trout',
    'R Gonzalez': 'Romy Gonzalez',
    'T Stephenson': 'Tyler Stephenson',
    'L Nootbaar': 'Lars Nootbaar',
    "L O'Hoppe": "Logan O'Hoppe",
    'N Cameron': 'Noah Cameron',
    'E Diaz': 'Edwin Díaz',
    'T Kahnle': 'Tommy Kahnle',
    'D Palencia': 'Daniel Palencia',
    'T Scott': 'Tanner Scott',
    'S Smith': 'Shane Smith',
    'B Walter': 'Brandon Walter',
    'L Castillo': 'Luis Castillo',
    'W Abreu': 'Wilyer Abreu',
    'Y Alvarez': 'Yordan Alvarez',
    'P Lopez': 'Pablo Lopez',
    # more names
    'C Raleigh': 'Cal Raleigh',
    'K Tucker': 'Kyle Tucker',
    'A Abbot': 'Austin Abbot',
    'S Ohtani': 'Shohei Ohtani'
} 

def copy_dict_to_df(data_dict, df, index):
    for key, value in data_dict.items():
        df.loc[index, key] = value
    return df

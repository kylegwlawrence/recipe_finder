import git

def recipe_to_github(filename):  
    repo = git.Repo('/Users/kylelawrence/Documents/recipe_finder') 
    # Do some changes and commit 
    repo.index.add([filename]) 
    print('Files Added Successfully') 
    repo.index.commit(f'Save {filename} to github') 
    print('Commited successfully')
    origin = repo.remote(name='origin')
    origin.push()
    print('Pushed changes to origin')

    github_link = f'https://github.com/kylegwlawrence/recipe_finder/blob/main/{filename}'
    return github_link

if __name__ == '__main__':
    f = 'md_recipes/recipes_vodkasauce-pasta-kale_3_20240311-144445_test.md'
    github_link = recipe_to_github(f)
    print(github_link)
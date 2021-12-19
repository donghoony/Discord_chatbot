import pickle

def save(f):
    with open("Cogs/Reinforce/reinforce.pkl", 'wb') as file:
        pickle.dump(f, file)

def load():
    try:
        with open("Cogs/Reinforce/reinforce.pkl", "rb") as file:
            data = pickle.load(file)
    except:
        data = {}
        save(data)
    return data

def save_result(item):
    items = load()
    items[item.owner_id] = item
    save(items)

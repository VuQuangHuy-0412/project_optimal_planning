#include <bits/stdc++.h>

using namespace std;

int MAX_SHAKING;

int N;
long long D;
vector<vector<int>> d, c;

void readData()
{
    cin >> N >> D;
    int tmp;
    for (int i = 0; i < N; i++)
    {
        vector<int> _d;
        for (int j = 0; j < N; j++)
        {
            cin >> tmp;
            _d.push_back(tmp);
        }
        d.push_back(_d);
    }
    for (int i = 0; i < N; i++)
    {
        vector<int> _c;
        for (int j = 0; j < N; j++)
        {
            cin >> tmp;
            _c.push_back(tmp);
        }
        c.push_back(_c);
    }
}

struct State
{
    vector<int> parent;
    vector<vector<int>> children;

    State()
    {
        parent = vector<int>(N, 0);
        for (int i = 1; i < N; i++)
        {
            parent[i] = i - 1;
        }
        children = vector<vector<int>>(N, vector<int>());
        for (int i = 1; i < N; i++)
        {
            children[i - 1].push_back(i);
        }
    }

    State(vector<int> _parent)
    {
        parent = _parent;
        children = vector<vector<int>>(N, vector<int>());
        for (int i = 1; i < N; i++)
        {
            children[parent[i]].push_back(i);
        }
    }

    long long calTimeDuration(int i);
    bool isValidSolution();
    long long getCost();
    vector<State> getAllNeighbors();
    pair<bool, State> localSearch();
    void write();
};

long long State::calTimeDuration(int i)
{
    long long result = 0ll;
    if (i == 0)
    {
        return result;
    }
    while (this->parent[i] != 0)
    {
        result += c[this->parent[i]][i];
        i = this->parent[i];
    }
    result += c[0][i];
    return result;
}

bool State::isValidSolution()
{
    for (int i = 1; i < N; i++)
    {
        if (this->calTimeDuration(i) > D)
        {
            return false;
        }
    }
    return true;
}

long long State::getCost()
{
    long long result = 0ll;
    for (int i = 1; i < N; i++)
    {
        result += c[this->parent[i]][i];
    }
    return result;
}

bool operator==(State a, State b)
{
    for (int i = 1; i < N; i++)
    {
        if (a.parent[i] != b.parent[i])
        {
            return false;
        }
    }
    return true;
}

template <typename T>
bool checkNotExists(vector<T> list, T object)
{
    for (auto element : list)
    {
        if (element == object)
        {
            return false;
        }
    }
    return true;
}

template <typename T>
T getRandom(vector<T> list)
{
    int length = list.size();
    int index = rand() % length;
    return list[index];
}

vector<State> State::getAllNeighbors()
{
    vector<State> result;
    for (int i = 1; i < N; i++)
    {
        vector<int> _parent = this->parent;
        int j = _parent[i];
        if ((int)children[j].size() > 1)
        {
            for (auto k : children[j])
            {
                if (k != i)
                {
                    _parent[i] = k;
                    State neighbor = State(_parent);
                    if (checkNotExists<State>(result, neighbor))
                    {
                        result.push_back(neighbor);
                    }
                }
            }
        }
        if (j != 0)
        {
            _parent[i] = _parent[j];
            State neighbor = State(_parent);
            if (checkNotExists<State>(result, neighbor))
            {
                result.push_back(neighbor);
            }
        }
    }
    return result;
}

pair<bool, State> State::localSearch()
{
    State result = *this;
    
    bool hasSolution = result.isValidSolution();
    vector<State> neighbors = result.getAllNeighbors();
    for (auto element : neighbors)
    {
        if (element.isValidSolution() && ((!hasSolution) || (element.getCost() < result.getCost())))
        {
            hasSolution = true;
            result = element;
        }
    }
    return make_pair(hasSolution, result);
}

vector<State> getMoreNeighbors(vector<State>& currentNeighbors, vector<State> latestNeighbors)
{
    vector<State> newNeighbors;
    int i = 0;
    for (auto element: latestNeighbors)
    {
        vector<State> neighbors = element.getAllNeighbors();
        for (auto neighbor: neighbors)
        {
            if (checkNotExists<State>(currentNeighbors, neighbor))
            {
                currentNeighbors.push_back(neighbor);
                if (checkNotExists<State>(newNeighbors, neighbor))
                {
                    newNeighbors.push_back(neighbor);
                }
            }
        }
    }
    return newNeighbors;
}

clock_t start;

bool outOfTimeLimit(float timeLimitInSeconds = 3600.0f)
{
    clock_t timer = clock();
    return ((float) timer - start) / CLOCKS_PER_SEC >= timeLimitInSeconds;
}

State bestState;

void variableNeighborhoodSearch()
{
    State currentState = State();
    bestState = currentState;
    vector<State> currentNeighborStructure = vector<State>{currentState};
    vector<State> latestNeighbors = vector<State>{currentState};
    int k = 1;
    while ((k <= MAX_SHAKING) && !outOfTimeLimit())
    {
        latestNeighbors = getMoreNeighbors(currentNeighborStructure, latestNeighbors);
        State randomState = getRandom<State>(currentNeighborStructure);
        pair<bool, State> localSearchResult = randomState.localSearch();
        if (localSearchResult.first && (localSearchResult.second.getCost() < bestState.getCost()))
        {
            currentState = localSearchResult.second;
            bestState = currentState;
            k = 1;
            currentNeighborStructure = vector<State>{currentState};
            latestNeighbors = vector<State>{currentState};
        }
        else
        {
            k += 1;
        }
    }
}

void State::write()
{
    if (this->isValidSolution())
    {
        for (int i = 1; i < N; i++)
        {
            cout << this->parent[i] << " -> " << i << " " << c[this->parent[i]][i] << endl;
        }
        cout << "Cost " << this->getCost() << endl;
    }
    else
    {
        cout << "No optimal solution!" << endl;
    }
}

int main()
{
    ios_base::sync_with_stdio(0);
    cin.tie(0);
    string inputDirectory = "D:\\Optimal\\project_optimal_planning\\DataSet\\";
    string outputDirectory = "D:\\Optimal\\project_optimal_planning\\Variable-Neighborhood-Search\\output\\";
    vector<pair<vector<string>, int>> fileNames = vector<pair<vector<string>, int>>{
        {{"data1.txt", "output1.txt"}, 2},
        {{"data2.txt", "output2.txt"}, 5},
        {{"data3.txt", "output3.txt"}, 5},
        {{"data4.txt", "output4.txt"}, 5},
        {{"data5.txt", "output5.txt"}, 5},
        {{"data6.txt", "output6.txt"}, 5},
        {{"data7.txt", "output7.txt"}, 5},
        {{"data8.txt", "output8.txt"}, 5},
        {{"data9.txt", "output9.txt"}, 5},
        {{"data10.txt", "output10.txt"}, 5}
    };
    for (auto p: fileNames)
    {
        string _inputFile = inputDirectory + p.first[0];
        const char* inputFile = _inputFile.c_str();
        freopen(inputFile, "r", stdin);
        string _outputFile = outputDirectory + p.first[1];
        const char* outputFile = _outputFile.c_str();
        freopen(outputFile, "w", stdout);
        // cout << inputFile << " " << outputFile << endl;
        readData();
        // cout << N << " " << D << endl;
        MAX_SHAKING = p.second;
        start = clock();
        variableNeighborhoodSearch();
        clock_t end = clock();
        bestState.write();
        cout << "Solving time: " << ((float) end - start) / CLOCKS_PER_SEC << endl;
    }
    return 0;
}

#include <iostream>
#include <vector>
#include <string>

class MaxHeap {
public:
    std::vector<int> V;

    // Constructor por defecto (inicia la cola vacía)
    MaxHeap() {}

private:
    int parent(int i) { return (i - 1) / 2; }
    int left(int i)   { return 2 * i + 1; }
    int right(int i)  { return 2 * i + 2; }

    // Repara la propiedad de Max-Heap hacia abajo (Shift-Down)
    void heapify(int i) {
        int m = i;
        int l = left(i);
        int r = right(i);

        if (l < V.size() && V[l] > V[m]) {
            m = l;
        }
        if (r < V.size() && V[r] > V[m]) {
            m = r;
        }
        if (m != i) {
            std::swap(V[i], V[m]);
            heapify(m);
        }
    }

    // Reparar propiedad max-heap hacia arriba
    void shift_up(int i) {
        while (i > 0 && V[parent(i)] < V[i]) { // criterio parada: Siempre que el padre de i menor a i (osea viola prop heap)
                                                // el i>0 
            std::swap(V[i], V[parent(i)]);
            i = parent(i);
        }
    }

public:
    // Operación insert(S, k)
    void insert(int k) {
        V.push_back(k);          // Inserta al final
        int i = V.size() - 1;
        shift_up(i);  // Reubica hacia arriba
    }

    // Operación extract-max(S)
    int extract_max() {
        if (V.empty()) return -1;

        int max_val = V[0];      // El máximo siempre está en la raíz
        V[0] = V.back();         // Reemplaza la raíz con el último elemento
        V.pop_back();            // Elimina el último elemento
        
        if (!V.empty()) {
            heapify(0);          // Restaura el orden desde la raíz
        }

        return max_val;

        // alternativamente, podríamos usar std::swap(V[0], V.back()); y luego V.pop_back(); para evitar la copia de elementos.
    }
};

int main() {
    // desincronizar con c
    std::ios_base::sync_with_stdio(false);
    std::cin.tie(NULL);

    MaxHeap heap;
    std::string command;

    while (std::cin >> command) {
        if (command == "end") {
            break;
        } else if (command == "insert") {
            int k;
            std::cin >> k;
            heap.insert(k);
        } else if (command == "extract") {
            std::cout << heap.extract_max() << "\n";
        }
    }

    return 0;
}
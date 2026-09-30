#include <iostream>
#include <cmath>
#include <vector>

class MaxHeap {
    public:
        std::vector<int> V; // Vector para guardar heap elements

        MaxHeap(std::vector<int> _V) { // constructor que recibe un vect de enteros
            V = _V;
        }

    private: // Private methods are not accessible from outside the class
        // example of accessing private methods from public methods
        // 

        int parent(int i) {
            return (i-1)/2;
        }

        int left(int i) {
            return 2 * i + 1; // porque +1? Poruqe el primer hijo de un nodo i es 2*i + 1, y el segundo hijo es 2*i + 2. Esto se debe a la forma en que se representan los árboles binarios en un arreglo.
        }

        int right(int i) {
            return 2 * i + 2;
        }

        void heapify(int i) { // Verificar con code de ppt 
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

    public:
        void build_heap() {
            for (int i = V.size()/2 - 1; i >= 0; i--) {
                heapify(i);
            }
        }
        void print_heap() {
            for (int i = 0; i < V.size(); i++) {
                std::cout << i <<": " << V[i] << " ";
            }
        }

};

int main() {
    std::vector<int> V = {4, 14, 10, 8, 2, 9, 3};

    MaxHeap heap(V);
    heap.print_heap();

    heap.build_heap();
    std::cout<<"\n";
    heap.print_heap();

    return 0;
}
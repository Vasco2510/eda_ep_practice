#include <iostream>


class Nodo {
    int data;
    Nodo *left;
    Nodo* right;

    void Nodo(int d, &l, &r){ # el constructor no puede tener i un tipo de dato.
                                # si tien tipo de dato, se reconoce como funcion. Eso no queremos
                    # los punteros tenia uq etener su tp ode dato Nodo* d=nullptr / por defecto 
        this->data = d;
        this->left = l;
        this->right = r;
    }

}
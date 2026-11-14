"""
dsu_rollback.py — Implementación de DSU con Rollback en Python puro.

Proyecto 2 AED: Algoritmos y Estructuras de Datos
Estructura: Disjoin Set Union (DSU) con Rollback

Esta implementación incluye las operaciones canónicas del TDA Conjuntos Disjuntos:
- make_set(x): crea un conjunto unitario {x} en O(1).
- find(x): busca el representante de x en O(log n) sin compresión de caminos.
- join(u, v): une los conjuntos de u y v por tamaño (Union by Size) en O(log n).
- snapshot(): captura el estado actual de la pila de historial en O(1).
- rollback(): revierte la última unión efectiva en O(1) estricto.

Todos los métodos principales son generadores que emiten eventos paso a paso
mediante (yield) para que la capa de animación (Manim) visualice cada operación.
"""


class DSURollback:
    """Disjoint Set Union (DSU) con soporte de Rollback en O(1).

    Eventos emitidos por make_set(x):
        ("make_set", x, parent_x, size_x, num_components)

    Eventos emitidos por find(x):
        ("find_start", x)
        ("find_step", current_node, parent_node)
        ("find_root", x, root_node)

    Eventos emitidos por join(u, v):
        ("join_start", u, v)
        ...eventos de find(u) y find(v)...
        ("join_roots", u, root_u, size_u, v, rv, size_v)
        ("join_redundant", u, v, common_root)          # si root_u == root_v
        ("push_history", child, old_parent, root, old_size, stack_len)
        ("join_merged", child, root, new_size, num_components)

    Eventos emitidos por rollback():
        ("rollback_start", stack_len)
        ("rollback_empty",)                             # si la pila está vacía
        ("pop_history", child, old_parent, root, old_size, stack_len)
        ("rollback_restored", child, old_parent, root, old_size, num_components)
    """

    def __init__(self, n: int, auto_init: bool = True):
        if n < 0:
            raise ValueError("El número de elementos n no puede ser negativo.")
        self.n = n
        self.parent = [-1] * n
        self.size = [0] * n
        self.active = [False] * n
        self.num_components = 0
        # Cada entrada en history es: (child, old_parent, root, old_size, old_components)
        self.history: list[tuple[int, int, int, int, int]] = []

        if auto_init:
            for i in range(n):
                for _ in self.make_set(i):
                    pass

    def make_set(self, x: int):
        """Crea el conjunto unitario {x} con parent[x] = x y size[x] = 1 en O(1).

        Yields:
            Tupla ("make_set", x, parent[x], size[x], num_components).
        """
        if x < 0 or x >= self.n:
            yield ("invalid_node", x)
            return False

        if not self.active[x]:
            self.active[x] = True
            self.num_components += 1
        self.parent[x] = x
        self.size[x] = 1
        yield ("make_set", x, self.parent[x], self.size[x], self.num_components)
        return True

    def get_root(self, x: int) -> int:
        """Obtiene la raíz de `x` sin emitir eventos (consulta interna)."""
        curr = x
        while self.parent[curr] != curr:
            curr = self.parent[curr]
        return curr

    def get_path(self, x: int) -> list[int]:
        """Retorna la lista de nodos desde `x` hasta su raíz."""
        path = [x]
        curr = x
        while self.parent[curr] != curr:
            curr = self.parent[curr]
            path.append(curr)
        return path

    def find(self, x: int):
        """Busca el representante (raíz) de `x` sin compresión de caminos.

        Complejidad: O(log n) en el peor caso gracias a Union by Size.

        Yields:
            Tuplas con los eventos del recorrido hacia la raíz.
        """
        if x < 0 or x >= self.n or not self.active[x]:
            yield ("invalid_node", x)
            return -1

        yield ("find_start", x)
        curr = x
        while self.parent[curr] != curr:
            nxt = self.parent[curr]
            yield ("find_step", curr, nxt)
            curr = nxt
        yield ("find_root", x, curr)
        return curr

    def join(self, u: int, v: int):
        """Une los conjuntos de `u` y `v` usando Union by Size y registra en la pila.

        Complejidad: O(log n) por búsqueda de raíces + O(1) para enlazar y apilar.

        Yields:
            Tuplas descriptivas de cada paso de la unión.
        """
        if (
            self.n == 0
            or u < 0
            or v < 0
            or u >= self.n
            or v >= self.n
            or not self.active[u]
            or not self.active[v]
        ):
            yield ("invalid_join", u, v)
            return False

        yield ("join_start", u, v)

        # Recorrer camino de u
        ru = u
        yield ("find_start", u)
        while self.parent[ru] != ru:
            nxt = self.parent[ru]
            yield ("find_step", ru, nxt)
            ru = nxt
        yield ("find_root", u, ru)

        # Recorrer camino de v
        rv = v
        yield ("find_start", v)
        while self.parent[rv] != rv:
            nxt = self.parent[rv]
            yield ("find_step", rv, nxt)
            rv = nxt
        yield ("find_root", v, rv)

        yield ("join_roots", u, ru, self.size[ru], v, rv, self.size[rv])

        # Caso borde: ambos nodos ya pertenecen al mismo conjunto
        if ru == rv:
            yield ("join_redundant", u, v, ru)
            return False

        # Union by Size: asegurar que ru sea la raíz de mayor o igual tamaño
        if self.size[ru] < self.size[rv]:
            ru, rv = rv, ru

        # Guardar estado previo en la pila de historial en O(1)
        record = (rv, self.parent[rv], ru, self.size[ru], self.num_components)
        self.history.append(record)
        yield ("push_history", rv, record[1], ru, record[3], len(self.history))

        # Enlazar raíz menor (rv) bajo raíz mayor (ru) en O(1)
        self.parent[rv] = ru
        self.size[ru] += self.size[rv]
        self.num_components -= 1

        yield ("join_merged", rv, ru, self.size[ru], self.num_components)
        return True

    def snapshot(self) -> int:
        """Retorna el tamaño actual de la pila como punto de control en O(1)."""
        return len(self.history)

    def rollback(self):
        """Deshace la última unión efectiva desapilando el tope de `history` en O(1).

        Yields:
            Tuplas con los eventos de la reversión.
        """
        yield ("rollback_start", len(self.history))

        if not self.history:
            yield ("rollback_empty",)
            return False

        child, old_p, root, old_sz, old_comp = self.history.pop()
        yield ("pop_history", child, old_p, root, old_sz, len(self.history))

        self.parent[child] = old_p
        self.size[root] = old_sz
        self.num_components = old_comp

        yield ("rollback_restored", child, old_p, root, old_sz, self.num_components)
        return True

    def rollback_to(self, snap: int):
        """Revierte todas las uniones realizadas después del punto `snap`."""
        while len(self.history) > snap:
            yield from self.rollback()


# =============================================================================
# Tests unitarios
# =============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("TESTS: Disjoin Set Union (DSU) con Rollback")
    print("=" * 60)

    # --- Test 1: Creación paso a paso con make_set(x) ---
    print("\n--- Test 1: Creación de conjuntos con make_set(x) ---")
    dsu = DSURollback(6, auto_init=False)
    for i in range(6):
        evts = list(dsu.make_set(i))
        print(f"  make_set({i}) -> {evts[0]}")
    assert dsu.num_components == 6
    assert dsu.parent == [0, 1, 2, 3, 4, 5]
    assert dsu.size == [1, 1, 1, 1, 1, 1]

    # --- Test 2: Uniones con Union by Size ---
    print("\n--- Test 2: Uniones con Union by Size ---")
    for pair in [(0, 1), (2, 3), (1, 3), (4, 5), (5, 3)]:
        evts = list(dsu.join(*pair))
        print(f"  join{pair} -> parent={dsu.parent}, size={dsu.size}, comps={dsu.num_components}")
    assert dsu.num_components == 1, "Debería quedar 1 sola componente"
    assert dsu.size[0] == 6, "La raíz 0 debería tener tamaño 6"

    # --- Test 3: Búsqueda find(3) sin compresión de caminos ---
    print("\n--- Test 3: Consulta find(3) sin compresión ---")
    f_evts = list(dsu.find(3))
    for e in f_evts:
        print(f"    {e}")
    assert dsu.parent[3] == 2, "No debe alterar parent[3] (sin compresión de caminos)"
    assert f_evts[-1] == ("find_root", 3, 0), "La raíz de 3 debe ser 0"

    # --- Test 4: Caso borde — Unión redundante en la misma componente ---
    print("\n--- Test 4: Caso borde — join(3, 5) redundante ---")
    r_evts = list(dsu.join(3, 5))
    assert r_evts[-1][0] == "join_redundant", "Debería detectar unión redundante"
    assert len(dsu.history) == 5, "La pila no debe crecer en una unión redundante"

    # --- Test 5: Snapshot y Rollback parcial / total ---
    print("\n--- Test 5: Rollback paso a paso ---")
    rb_evts = list(dsu.rollback_to(3))
    assert dsu.num_components == 3, "Tras revertir a snap=3 deben quedar 3 componentes"
    assert len(dsu.history) == 3

    list(dsu.rollback_to(0))
    assert dsu.parent == [0, 1, 2, 3, 4, 5], "Debe restaurar el arreglo parent original"
    assert dsu.size == [1, 1, 1, 1, 1, 1], "Debe restaurar el arreglo size original"
    assert dsu.num_components == 6

    # --- Test 6: Caso borde — Rollback con pila vacía ---
    print("\n--- Test 6: Caso borde — rollback() con pila vacía ---")
    e_evts = list(dsu.rollback())
    assert e_evts[-1][0] == "rollback_empty", "Debería emitir evento rollback_empty"

    print("\n" + "=" * 60)
    print("TODOS LOS TESTS PASARON [OK]")
    print("=" * 60)

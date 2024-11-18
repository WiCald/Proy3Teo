import yaml

with open("recognizer_mt.yaml", "r") as file:
    try:
        config = yaml.safe_load(file)
        print("Archivo YAML cargado correctamente.")
    except yaml.YAMLError as e:
        print(f"Error en el archivo YAML")

class TuringMachine:
    def __init__(self, yaml_config):
        # Leer configuración desde el archivo YAML
        with open(yaml_config, 'r') as file:
            self.config = yaml.safe_load(file)
        
        print("Contenido cargado desde YAML:", self.config.keys())  # Depuración

        self.q_states = self.config['q_states']['q_list']
        self.initial_state = self.config['q_states']['initial']
        self.final_state = self.config['q_states']['final']
        self.alphabet = self.config['alphabet']
        self.tape_alphabet = self.config['tape_alphabet']
        self.transitions = self.config['delta']
        self.simulation_strings = self.config['simulation_strings']
        self.blank_symbol = '#'  # Representa el símbolo vacío
        self.current_state = self.initial_state
        self.tape = []
        self.head_position = 0

        # Validar el YAML
        self.validate_yaml()

    def validate_yaml(self):
        # Verificar claves principales en el archivo YAML
        required_keys = ['q_states', 'alphabet', 'tape_alphabet', 'delta', 'simulation_strings']
        missing_keys = [key for key in required_keys if key not in self.config]
        if missing_keys:
            raise ValueError(f"Faltan claves requeridas en el YAML: {missing_keys}")

        # Validar delta
        if not isinstance(self.config['delta'], list) or len(self.config['delta']) == 0:
            raise ValueError("La clave 'delta' debe ser una lista no vacía de transiciones.")

        # Validar transiciones dentro de delta
        for transition in self.config['delta']:
            if not isinstance(transition, dict):
                raise ValueError(f"Transición inválida: {transition}")
            if 'params' not in transition or 'output' not in transition:
                raise ValueError(f"Falta 'params' u 'output' en la transición: {transition}")
            if 'initial_state' not in transition['params'] or 'tape_input' not in transition['params']:
                raise ValueError(f"Faltan claves en 'params': {transition['params']}")
            if 'final_state' not in transition['output'] or 'tape_output' not in transition['output']:
                raise ValueError(f"Faltan claves en 'output': {transition['output']}")

    def load_tape(self, input_string):
        # Inicializar la cinta con la cadena de entrada
        self.tape = list(input_string)
        self.tape.append(self.blank_symbol)  # Agregar el símbolo vacío al final
        self.head_position = 0

    def simulate(self, input_string):
        # Cargar la cinta con la cadena de entrada
        self.load_tape(input_string)
        self.current_state = self.initial_state
        ids = []  # Lista para almacenar descripciones instantáneas

        while True:
            current_symbol = self.tape[self.head_position]
            # Buscar transición válida
            transition = self.find_transition(self.current_state, current_symbol)
            
            # Guardar la descripción instantánea
            ids.append(self.get_instantaneous_description())

            if not transition:
                # No hay transición válida
                break

            # Aplicar la transición
            self.apply_transition(transition)

            # Revisar si alcanzó el estado final
            if self.current_state == self.final_state:
                ids.append(self.get_instantaneous_description())
                break

        # Determinar si la cadena es aceptada
        accepted = self.current_state == self.final_state
        return ids, accepted

    def find_transition(self, state, symbol):
        # Buscar una transición válida para el estado y símbolo actual
        for transition in self.transitions:
            if transition['params']['initial_state'] == state and transition['params']['tape_input'] == symbol:
                return transition
        return None

    def apply_transition(self, transition):
        # Aplicar la transición al estado y a la cinta
        self.current_state = transition['output']['final_state']
        tape_output = transition['output'].get('tape_output', self.blank_symbol)  # Default: blank_symbol
        tape_displacement = transition['output']['tape_displacement']

        # Validar tape_output
        if tape_output is None or tape_output not in self.tape_alphabet:
            raise ValueError(f"tape_output inválido: {tape_output}. Verifica las transiciones en tu YAML.")

        # Actualizar la cinta
        self.tape[self.head_position] = tape_output

        # Mover la cabeza lectora
        if tape_displacement == 'R':
            self.head_position += 1
            if self.head_position == len(self.tape):
                self.tape.append(self.blank_symbol)
        elif tape_displacement == 'L':
            self.head_position -= 1
            if self.head_position < 0:
                self.tape.insert(0, self.blank_symbol)
                self.head_position = 0

    def get_instantaneous_description(self):
        # Generar la descripción instantánea
        tape_str = ''.join(self.tape)
        return f"State: {self.current_state}, Tape: {tape_str}, Head Position: {self.head_position}"

# Main: Ejecutar ambas máquinas de Turing
def main():
    print("=== Simulador de Máquina de Turing ===")
    # Archivo YAML de configuración
    yaml_file_recognizer = "recognizer_mt.yaml"
    yaml_file_alterer = "alterer_mt.yaml"
    
    # Máquina reconocedora
    print("\n--- Máquina Reconocedora ---")
    tm_recognizer = TuringMachine(yaml_file_recognizer)
    for string in tm_recognizer.simulation_strings:
        print(f"\nSimulando entrada: {string}")
        ids, accepted = tm_recognizer.simulate(string)
        for id in ids:
            print(id)
        print(f"Resultado: {'Aceptada' if accepted else 'Rechazada'}")

    # Máquina alteradora
    print("\n--- Máquina Alteradora ---")
    tm_alterer = TuringMachine(yaml_file_alterer)
    for string in tm_alterer.simulation_strings:
        print(f"\nSimulando entrada: {string}")
        ids, _ = tm_alterer.simulate(string)
        for id in ids:
            print(id)
        print(f"Resultado final de la cinta: {''.join(tm_alterer.tape).strip(tm_alterer.blank_symbol)}")

if __name__ == "__main__":
    main()

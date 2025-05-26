
**Tarefas Detalhadas da Fase 2:**

1.  **Implementar `mea.mea.MEA` (Módulo MEA):**
    *   **Classe `MEA`**:
        *   **Inicialização:** Aceitar uma configuração de layout dos eletrodos (e.g., uma lista de coordenadas (x,y,z) para cada eletrodo, ou parâmetros para gerar layouts comuns como grids).
        *   **Atributos:** Armazenar as posições dos eletrodos, número de eletrodos.
        *   **Métodos Utilitários (Exemplos):**
            *   `get_electrode_position(electrode_id)`: Retorna a coordenada de um eletrodo específico.
            *   `get_neurons_near_electrode(organoid, electrode_id, radius)`: Dada uma instância de `Organoid`, um ID de eletrodo e um raio, retorna os índices (ou uma referência) dos neurônios do organoide que estão dentro desse raio do eletrodo. Isso será crucial para estímulo e leitura direcionados.
            *   (Opcional) Funções para visualizar o layout do MEA, talvez sobreposto a um plot do organoide.

2.  **Implementar `electrophysiology.stimulus_generator` (Gerador de Estímulos):**
    *   **Funções para Criar Estímulos Brian2:**
        *   `create_pulse_train(amplitude, frequency, pulse_width, duration, dt)`: Gera um `brian2.TimedArray` representando um trem de pulsos de corrente.
        *   `create_current_step(amplitude, onset, offset, dt)`: Gera um degrau de corrente.
        *   `create_ramp_current(start_amplitude, end_amplitude, duration, dt)`: Gera uma rampa de corrente.
        *   `create_sinusoidal_current(amplitude, frequency, phase, duration, dt)`: Gera uma corrente senoidal.
        *   (Opcional) Funções para estímulos mais complexos ou baseados em arquivos.
    *   Todas as funções devem retornar um `brian2.TimedArray` ou um formato compatível para ser usado como corrente de entrada (`I_input` ou `I`) nos neurônios.

3.  **Expandir `simulation.simulator.Simulator` para Integração com MEA e Estímulos:**
    *   **Modificar `__init__`:** Opcionalmente aceitar uma instância de `MEA`.
    *   **Método `set_mea(mea_instance)`:** Para associar uma MEA ao simulador após a inicialização.
    *   **Método `add_stimulus(electrode_id, stimulus_waveform, target_group_name, influence_radius, start_time=0*b2.ms)`:**
        *   Usa o `MEA` e o `Organoid` para identificar os neurônios alvo próximos ao `electrode_id` dentro do `influence_radius`.
        *   Modifica a corrente de entrada (`I_input` ou um campo de corrente de estímulo dedicado) desses neurônios alvo para injetar a `stimulus_waveform` (que é um `TimedArray`).
        *   Pode precisar adicionar um novo subgrupo ou um parâmetro de `NeuronGroup` para a corrente de estímulo se `I_input` já for usado por sinapses.
        *   O `start_time` permitiria escalonar o início do estímulo.

4.  **Implementar `electrophysiology.data_persistence` (Persistência de Dados com SQLite):**
    *   **`db_schema.py`:**
        *   Definir o esquema do banco de dados SQLite:
            *   Tabela `Simulations` (ID da simulação, timestamp, parâmetros principais, notas).
            *   Tabela `NeuronGroups` (ID da simulação, nome do grupo, tipo de neurônio, número de neurônios, parâmetros do modelo).
            *   Tabela `SynapsesInfo` (ID da simulação, nome do grupo sináptico, tipo, grupos pré/pós).
            *   Tabela `Stimuli` (ID da simulação, ID do estímulo, tipo de estímulo, eletrodo alvo, parâmetros).
            *   Tabela `SpikeData` (ID da simulação, ID do neurônio, tempo do spike).
            *   Tabela `StateData` (ID da simulação, ID do neurônio, nome da variável, tempo, valor).
            *   (Opcional) Tabelas para armazenar posições, conectividade, etc.
        *   Função `create_tables(db_connection)` para criar essas tabelas se não existirem.
    *   **`sqlite_writer.py`:**
        *   **Classe `SQLiteWriter`**:
            *   `__init__(db_path)`: Conecta ao DB, chama `create_tables`.
            *   `log_simulation_start(...)`: Registra uma nova simulação na tabela `Simulations` e retorna o `sim_id`.
            *   `log_neuron_group_info(...)`.
            *   `log_synapse_info(...)`.
            *   `log_stimulus_info(...)`.
            *   `store_spike_data(sim_id, spike_monitor_object, group_name_identifier)`: Extrai dados do `SpikeMonitor` e salva.
            *   `store_state_data(sim_id, state_monitor_object, group_name_identifier)`: Extrai dados do `StateMonitor` e salva.
            *   `close_connection()`.
    *   **Integrar `SQLiteWriter` no `Simulator`:**
        *   `Simulator.__init__` opcionalmente aceita `db_path`. Se fornecido, instancia `SQLiteWriter`.
        *   `Simulator.setup_simulation_entry(...)`: Chama `sqlite_writer.log_simulation_start(...)` e armazena o `sim_id`.
        *   `Simulator.run()`: Após a execução da simulação Brian2, chama os métodos apropriados do `sqlite_writer` para salvar os dados dos monitores, associando-os ao `sim_id` atual.
        *   Método `close()` no `Simulator` para fechar a conexão com o DB.

5.  **Expandir Capacidades de "Leitura" do MEA (Conceitual/LFP Proxy):**
    *   **No `Simulator.add_recording` ou um novo método:**
        *   Permitir a configuração de um "monitor de LFP proxy" para um eletrodo MEA.
        *   Isso pode envolver:
            *   Identificar neurônios próximos ao eletrodo.
            *   Criar um `StateMonitor` que some as correntes sinápticas nesses neurônios (se os modelos sinápticos as expuserem e os modelos neuronais tiverem termos de corrente sináptica separados).
            *   OU, usar uma `NetworkOperation` (`run_regularly`) que calcula uma média ponderada do `Vm` ou outra medida agregada dos neurônios próximos e armazena isso em um `TimedArray` ou um `StateMonitor` de um `NeuronGroup` fictício.
    *   **`sqlite_writer.py`:** Adicionar métodos para salvar esses dados de LFP proxy.

6.  **Exemplos e Testes:**
    *   Desenvolver Notebooks de Exemplo:
        *   `05_MEA_Stimulation_and_Basic_Recording.ipynb`
        *   `06_Simulating_Spontaneous_Activity_and_LFP_Proxy.ipynb`
        *   `07_Patterned_Stimulation_and_Response_Analysis.ipynb`
        *   `11_Data_Persistence_Saving_and_Loading_with_SQLite.ipynb` (pode precisar do `sqlite_reader.py` também).
    *   Escrever testes unitários e de integração para as novas funcionalidades de MEA, geração de estímulos e persistência de dados.

7.  **Documentação:**
    *   Atualizar docstrings para todas as novas classes e métodos.
    *   Expandir a documentação Sphinx com guias sobre como usar as funcionalidades de MEA, estímulo e salvamento de dados.

Esta fase adiciona uma camada significativa de realismo experimental e gerenciamento de dados ao `pyneurorg`.

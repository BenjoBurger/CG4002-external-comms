# Setup Instructions

## 1. Start the Evaluation Server

1. Open a terminal (**T1**) for the evaluation server.
2. Execute the following command:
   ```
   bash run_server.sh
   ```

## 2. Open the Evaluation Server Client

1. Open a browser (**B1**) and navigate to the evaluation server client.
2. Log in.
3. Take note of the **port number** displayed on the screen after logging in.

## 3. Set Up Reverse Tunneling to the Evaluation Server

1. Open another terminal (**T2**).
2. Run the following command, replacing `[port number]` with the number noted in the previous step:
   ```
   ssh -R 8888:localhost:[port number] xilinx@makerslab-fpga-29.d2.comp.nus.edu.sg
   ```

## 4. Set Up SSH Tunneling for Jupyter Notebooks

1. Open another terminal (**T3**).
2. Run the following command:
   ```
   ssh -L 9090:localhost:9090 xilinx@makerslab-fpga-29.d2.comp.nus.edu.sg
   ```

## 5. Open and Run Jupyter Notebooks

1. Open a browser (**B2**) and navigate to:
   ```
   localhost:9090
   ```
2. Locate `ai_main_process.py` and run the **AI server**.

## 6. Run the Main Code

1. In either **T2** or **T3**, navigate to the external communications directory:
   ```
   cd CG4002-external-comms
   ```
2. Run the main code using:
   ```
   sudo -E python main.py
   ```
3. Enter the **port number** `8888` when prompted and press **Enter**.

## 7. Start the Relay Client Process

1. Open another terminal (**T4**).
2. Run the following command in the ```relay_node``` directory:
   ```
   python RelayClientProcess.py
   ```


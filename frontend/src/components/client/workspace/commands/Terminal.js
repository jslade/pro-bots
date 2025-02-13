import React, { useCallback, useContext, useEffect, useState } from 'react';
import Terminal, { ColorMode, TerminalOutput } from 'react-terminal-ui';

import { ApiContext } from '../../../../contexts/ApiContext';
import './Terminal.css';

const TerminalComponent = () => {
    const api = useContext(ApiContext);
    const [terminalLineData, setTerminalLineData] = useState([]);

    const [input, setInput] = useState('');
    const [history, setHistory] = useState([]);
    const [historyIndex, setHistoryIndex] = useState(-1);
  
    const handleCommand = (command) => {
        // Process the command
        if (command === 'clear') {
            setTerminalLineData([]);
        } else if (command === '') {
        } else {
            // Show the input line
            setTerminalLineData([
                ...terminalLineData,
                <TerminalOutput key={terminalLineData.length}>
                &gt;&gt;&gt;&nbsp;{command}
                </TerminalOutput>,
            ])

            sendCommand(command);
            addToHistory(command)
        }
    };
  
    const sendCommand = useCallback((command) => {
        // Send the input to the server
        api.sendMessage('terminal', 'input', {
            input: command,
        });
    }, [api]);

    const addToHistory = useCallback((command) => {
        // Add to the history -- if it's not the same as the last command
        if (history.length > 0 && command != history[-1]) {
            setHistory([...history, command]);
        }
        setHistoryIndex(-1); // Reset to -1 to indicate we're back at the current input
        setInput(''); // Clear the input after command execution
    }, [history, setHistory, setHistoryIndex, setInput])

    const handleKeyDown = (event) => {
        console.log(event.key);
        if (event.key === 'ArrowUp') {
            event.preventDefault();
            let newIndex = historyIndex + 1;
            if (newIndex < history.length) {
                setInput(history[history.length - 1 - newIndex]);
                setHistoryIndex(newIndex);
            }
        }
        if (event.key === 'ArrowDown') {
            event.preventDefault();
            let newIndex = historyIndex - 1;
            if (newIndex >= 0) {
                setInput(history[history.length - 1 - newIndex]);
                setHistoryIndex(newIndex);
            }
        }
    };
  
    const onOutput = useCallback((output) => {
        setTerminalLineData([
            ...terminalLineData,
            <TerminalOutput key={terminalLineData.length}>
            {output}
            </TerminalOutput>,
        ])
    }, [terminalLineData]);

    useEffect(() => {
        if (!api) return;

        api.registerCallback('terminal', 'output', (data) => {
            onOutput(data.output);
        });
    }, [api, api?.registerCallback, onOutput]);


    return (
        <div className="container">
        <Terminal
            name="Command Terminal"
            colorMode={ColorMode.Dark}
            TopButtonsPanel={()=> null}
            height="20em"
            prompt=">>>"
            onInput={handleCommand}
            startingInputValue={input}
        >
            {terminalLineData}
        </Terminal>
        </div>
    );
};

export { TerminalComponent }
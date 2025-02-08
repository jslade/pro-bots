import React, { useCallback, useContext, useEffect, useState } from 'react';
import Terminal, { ColorMode, TerminalOutput } from 'react-terminal-ui';

import { ApiContext } from '../../../ApiContext';
import './Terminal.css';

function formatWithLeadingZeros(number, places) {
    return `${number.toString().padStart(places ? places : 2, '0')}`;
}

const TerminalComponent = () => {
    const api = useContext(ApiContext);
    const [terminalLineData, setTerminalLineData] = useState([]);

    const onInput = useCallback((terminalInput) => {
        if (terminalInput === 'clear') {
            setTerminalLineData([]);
        } else if (terminalInput === '') {
        } else {
            // Show the input line
            setTerminalLineData([
                ...terminalLineData,
                <TerminalOutput key={terminalInput.length}>
                &gt;&gt;&gt;&nbsp;{terminalInput}
                </TerminalOutput>,
            ])

            // Send the input to the server
            api.sendMessage('terminal', 'input', {
                input: terminalInput,
            });
        }
    }, [api, terminalLineData])

    const onOutput = useCallback((output) => {
        setTerminalLineData([
            ...terminalLineData,
            <TerminalOutput key={terminalLineData.length}>
            {output}
            </TerminalOutput>,
        ])
    }, [terminalLineData]);

    useEffect(() => {
        api.registerCallback('terminal', 'output', (data) => {
            onOutput(data.output);
        });
    }, [api, api.registerCallback, onOutput]);


    return (
        <div className="container">
        <Terminal
            name=""
            colorMode={ColorMode.Dark}
            TopButtonsPanel={()=> null}
            prompt=">>>"
            onInput={onInput}
        >
            {terminalLineData}
        </Terminal>
        </div>
    );
};

export { TerminalComponent }
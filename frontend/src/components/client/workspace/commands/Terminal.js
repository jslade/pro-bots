import React, { useCallback, useContext, useEffect, useState, useRef, useMemo } from 'react';
import { Box, Grid, Typography, Paper, TextField } from '@mui/material';

import { ApiContext } from '../../../../contexts/ApiContext';
import './Terminal.css';

const PROMPT = '>>> ';

const TerminalComponent = ({ promptRef }) => {
    const api = useContext(ApiContext);
    const [lines, setLines] = useState([]);

    const [input, setInput] = useState('');
    const [history, setHistory] = useState([]);
    const [historyIndex, setHistoryIndex] = useState(-1);

    const scrollRef = useRef(null);

    const handleKeyPress = (e) => {
        if (e.key === 'Enter') {
            const command = input;
            setInput('');
            handleInput(command);
            return;
        }

        if (e.key === 'ArrowUp') {
            if (historyIndex === -1) {
                setHistoryIndex(history.length - 1);
                setInput(history[history.length - 1] || '');
            } else if (historyIndex === 0) {
                setHistoryIndex(-1);
                setInput('');
            } else {
                setHistoryIndex(historyIndex - 1);
                setInput(history[historyIndex - 1] || '');
            }
            e.preventDefault();
            return;
        }
        if (e.key === 'ArrowDown') {
            if (historyIndex < history.length - 1) {
                setHistoryIndex(historyIndex + 1);
                setInput(history[historyIndex + 1] || '');
            } else {
                setHistoryIndex(-1);
                setInput('');
            }
            e.preventDefault();
            return;
        }
    };

    const handleInput = (command) => {
        if (command === 'clear') {
            setLines([]);
        } else if (command === '') {
        } else {
            setLines([
                ...lines, `${PROMPT} ${command}`
            ])

            sendCommand(command);
            addToHistory(command)
        }
    };

    const sendCommand = useCallback((command) => {
        api.sendMessage('terminal', 'input', {
            input: command,
        });
    }, [api]);

    const addToHistory = useCallback((command) => {
        let newHistory = history;
        if (history.length === 0 || command !== history[-1]) {
            newHistory = [...history, command];
            setHistory(newHistory);
        }
        const newIndex = -1; 
        setHistoryIndex(newIndex);
    }, [history, setHistory, setHistoryIndex])

    const onOutput = useCallback((output) => {
        setLines([...lines, output]);
    }, [lines]);

    useEffect(() => {
        if (!api) return;

        api.registerCallback('terminal', 'output', (data) => {
            onOutput(data.output);
        });

        return () => {
            api.unregisterCallback('terminal', 'output');
        }
    }, [api, api?.registerCallback, onOutput]);


    // Scroll to the bottom whenever terminalLines changes
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [lines]);

    const renderLines = useMemo(() => {
        return lines.map((line, index) => {
            return (
                <div key={index} className="line">
                    {line}
                </div>
            );
        });
    }, [lines]);

    return (
        <Grid container direction="column" className="container" sx={{  }}>
            <Grid item sx={{ flex: 1, overflow: 'auto' }} className="content">
                <Paper elevation={3} sx={{
                    height: '100%', p: 1,
                    backgroundColor: '#252222', color: '#efefef',
                    fontFamily: 'monospace', fontSize: '1em',
                    borderRadius: '0px',
                    overflow: 'auto',
                    }}>
                    {renderLines}
                </Paper>
            </Grid>
            <Grid item>
                <Box sx={{ 
                    display: 'flex', p: 0, alignItems: 'center',
                    position: 'sticky', bottom: 0, width: '100%',
                    }}>
                    <Typography variant="body1" sx={{
                        p: 1,
                        backgroundColor: '#252222', color: '#efefef',
                        fontFamily: 'monospace', fontSize: '1em',
                    }}>{PROMPT}</Typography>
                    <TextField
                        fullWidth
                        variant="standard"
                        inputRef={promptRef}
                        InputProps={{
                            disableUnderline: true,
                            style: {
                                padding: 0,
                                fontFamily: 'monospace', fontSize: '1em',
                                backgroundColor: '#252222', color: '#efefef',
                            },
                        }}
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => {handleKeyPress(e)}}
                        placeholder="Enter command..."
                    />
                </Box>
            </Grid>
            <div ref={scrollRef} style={{paddingBottom: '0em'}}/>
        </Grid>
    );
};

export default TerminalComponent;
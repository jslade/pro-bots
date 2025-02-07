import React, { useContext, useEffect, useState } from 'react';
import useWebSocket, { ReadyState } from 'react-use-websocket';

import { Grid, Box } from '@mui/material';

import { SessionContext } from '../SessionContext';
import ProgrammingSpace from './ProgrammingSpace';
import CommandSpace from './CommandSpace';
import HUD from './HUD';

const WS_BASE = `ws://${window.location.hostname}:5001`;

const Workspace = () => {
    const session = useContext(SessionContext);
    const [connected, setConnected] = React.useState(false);

    const { sendJsonMessage, lastJsonMessage, readyState } = useWebSocket(
        WS_BASE, {
            share: false,
            shouldReconnect: () => true,
        },
    )
    
    useEffect(() => {
        console.log("Connection state changed", readyState)
        if (readyState === ReadyState.OPEN && !connected) {
            setConnected(true);
            sendJsonMessage({
                event: "connected",
                sessionId: session.sessionId,
                data: { message: "Hello, world!",  },
            })
        }
        if ((readyState === ReadyState.CONNECTING || readyState === ReadyState.CLOSED)
             && connected) {
            setConnected(false);
        }
    }, [readyState, sendJsonMessage, session.sessionId, connected])
    
    useEffect(() => {
        if (!lastJsonMessage) return;
        console.log("message:", lastJsonMessage)
    }, [lastJsonMessage])
    
    return ( <>
        <Grid item xs={12} style={{ height: '1.5em' }}>
            <Box display="flex" flexDirection="column" height="100%">
                <Box flex={1} border={1}>
                    {connected ? 'Connected' : 'Disconnected'}
                </Box>
            </Box>
        </Grid>
        <Grid container spacing={2} style={{ height: 'calc(100vh - 1.5em)' }}>
            <Grid item xs={6}>
                <Box display="flex" flexDirection="column" height="100%">
                    <Box flex={1} border={1}>
                        <ProgrammingSpace />
                    </Box>
                    <Box flex={1} border={1}>
                        <CommandSpace />
                    </Box>
                </Box>
            </Grid>
            <Grid item xs={6}>
                <Box height="100%" border={1}>
                    <HUD />
                </Box>
            </Grid>
        </Grid>
    </>);
};

export default Workspace;

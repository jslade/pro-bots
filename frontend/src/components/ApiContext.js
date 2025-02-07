import React, { createContext, useContext, useState, useEffect } from 'react';
import useWebSocket, { ReadyState } from 'react-use-websocket';

import {
    QueryClient,
    QueryClientProvider,
} from '@tanstack/react-query'

import { SessionContext } from './SessionContext';

const WS_BASE = `ws://${window.location.hostname}:5001`;

const queryClient = new QueryClient()

const ApiContext = createContext();

const ApiProvider = ({ children }) => {
    const session = useContext(SessionContext);

    const { sendJsonMessage, lastJsonMessage, readyState } = useWebSocket(
        WS_BASE, {
            share: false,
            shouldReconnect: () => true,
        },
    )
    
    useEffect(() => {
        if (!session.sessionId) return;

        console.log("Connection state changed", readyState)
        if (readyState === ReadyState.OPEN && !session.connected) {
            session.setConnected(true);
            sendJsonMessage({
                type: "session",
                event: "connected",
                sessionId: session.sessionId,
                data: { message: "Hello, world!",  },
            })
        }
        if ((readyState === ReadyState.CONNECTING || readyState === ReadyState.CLOSED)
             && session.connected) {
            session.setConnected(false);
        }
    }, [
        readyState,
        sendJsonMessage,
        session, session.sessionId,
        session.connected, session.setConnected
    ])
    
    useEffect(() => {
        if (!lastJsonMessage) return;
        console.log("message:", lastJsonMessage)
    }, [lastJsonMessage])

    return (
        <ApiContext.Provider value={{ }}>
            <QueryClientProvider client={queryClient}>
                {children}
            </QueryClientProvider>
        </ApiContext.Provider>
    );
};

export { ApiContext, ApiProvider };

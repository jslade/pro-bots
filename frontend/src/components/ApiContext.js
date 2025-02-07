import React, {
    createContext,
    useCallback,
    useContext,
    useEffect,
    useRef,
    useState,
} from 'react';
import useWebSocket, { ReadyState } from 'react-use-websocket';

import {
    QueryClient,
    QueryClientProvider,
} from '@tanstack/react-query'

import { SessionContext } from './SessionContext';

const WS_BASE = `ws://${window.location.hostname}:5001`;

const queryClient = new QueryClient()

const ApiContext = createContext();

/**
 * @description
 * This component uses WebSocket to manage API communication and provides
 * methods to send messages and register callbacks for specific message types and events.
 * 
 * It provides a consistent way of sending and receiving messages, defining the
 * message structure, and handling connection state. When messages are received,
 * they are dispatched to the appropriate handlers based on their type and event.
 * 
 * @provides
 * - `sendMessage` function to send JSON messages via WebSocket.
 * - `registerCallback` function to register handlers for specific message types and events.
 */
const ApiProvider = ({ children }) => {
    const session = useContext(SessionContext);
    const [prevReadyState, setPrevReadyState] = useState(ReadyState.CONNECTING);
    const dispatchRef = useRef({});

    const { sendJsonMessage, lastJsonMessage, readyState } = useWebSocket(
        WS_BASE, {
            share: false,
            shouldReconnect: () => true,
        },
    )
    
    const sendMessage = useCallback((type, event, data) => {
        if (!session.sessionId) return;

        const message = {
            type,
            event,
            sessionId: session.sessionId,
            data: data ? data : {},
        };
        console.log("Sending message", message);
        sendJsonMessage(message);

    }, [session.sessionId, sendJsonMessage]);

    const registerCallback = useCallback((type, event, handler) => {
        const key = `${type}:${event ? event : ''}`;
        if (!dispatchRef.current[key]) {
            dispatchRef.current[key] = [];
        }

        dispatchRef.current[key].add(handler);
    }, []);

    useEffect(() => {
        if (!session.sessionId) return;

        if (prevReadyState !== readyState) {
            console.log("Connection state changed", readyState)
            setPrevReadyState(readyState);
        }

        if (readyState === ReadyState.OPEN && !session.connected) {
            session.setConnected(true);
            sendMessage("session", "connected")
        }
        if ((readyState === ReadyState.CONNECTING || readyState === ReadyState.CLOSED)
             && session.connected) {
            session.setConnected(false);
        }
    }, [
        readyState,
        prevReadyState, setPrevReadyState,
        sendMessage,
        session, session.sessionId,
        session.connected, session.setConnected
    ])
    
    useEffect(() => {
        if (!lastJsonMessage) return;

        console.log("Received message", lastJsonMessage);

        const { type, event } = lastJsonMessage;

        // For handlers that are specific to a type and event
        const type_event_key = `${type}:${event}`;
        if (dispatchRef.current[type_event_key]) {
            dispatchRef.current[type_event_key]?.forEach(handler => handler(lastJsonMessage));
        }

        // For handlers that are for all event of a type
        const type_key = `${type}:`;
        if (dispatchRef.current[type_key]) {
            dispatchRef.current[type_key]?.forEach(handler => handler(lastJsonMessage));
        }

    }, [lastJsonMessage])

    return (
        <ApiContext.Provider value={{ sendMessage, registerCallback }}>
            <QueryClientProvider client={queryClient}>
                {children}
            </QueryClientProvider>
        </ApiContext.Provider>
    );
};

export { ApiContext, ApiProvider };

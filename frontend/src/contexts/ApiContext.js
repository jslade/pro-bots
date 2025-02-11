import React, {
    createContext,
    useCallback,
    useContext,
    useEffect,
    useRef,
    useState,
} from 'react';
import useWebSocket, { ReadyState } from 'react-use-websocket';

import { SessionContext } from './SessionContext';

const WS_BASE = `ws://${window.location.hostname}:5001`;

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
    const [connected, setConnected] = useState(false);
    const [accepted, setAccepted] = useState(false);
    const dispatchRef = useRef({});

    const { sendJsonMessage, lastJsonMessage, readyState } = useWebSocket(
        WS_BASE, {
            share: false,
            shouldReconnect: () => true,
        },
    );
    
    const sendMessage = useCallback((type, event, data) => {
        if (!connected) return;

        const message = {
            type,
            event,
            sessionId: session.sessionId,
            data: data ? data : {},
        };
        console.log("Sending message", message);
        sendJsonMessage(message);

    }, [session?.sessionId, connected, sendJsonMessage]);

    const registerCallback = useCallback((type, event, handler) => {
        const key = `${type}:${event ? event : ''}`;
        if (!dispatchRef.current[key]) {
            dispatchRef.current[key] = [];
        }

        dispatchRef.current[key].push(handler);
    }, []);

    useEffect(() => {
        if (!session?.sessionId) return;

        if (prevReadyState !== readyState) {
            console.log("Connection state changed", readyState)
            setPrevReadyState(readyState);
        }

        if (readyState === ReadyState.OPEN && !session.connected) {
            setConnected(true);
            sendMessage("connection", "connected")
        }
        if ((readyState === ReadyState.CONNECTING || readyState === ReadyState.CLOSED)
             && session.connected) {
            setConnected(false);
            setAccepted(false);
        }
    }, [
        readyState,
        prevReadyState, setPrevReadyState,
        sendMessage,
        session, session.sessionId,
        connected, setConnected
    ])
    
    useEffect(() => {
        if (!lastJsonMessage) return;

        //console.log("Received message", lastJsonMessage);

        const { type, event, data } = lastJsonMessage;

        // For handlers that are specific to a type and event
        const type_event_key = `${type}:${event}`;
        if (dispatchRef.current[type_event_key]) {
            dispatchRef.current[type_event_key]?.forEach(handler => handler(data, type, event));
        }

        // For handlers that are for all event of a type
        const type_key = `${type}:`;
        if (dispatchRef.current[type_key]) {
            dispatchRef.current[type_key]?.forEach(handler => handler(data, type, event));
        }

    }, [lastJsonMessage])

    const sessionAccepted = useCallback(() => {
        console.log("SESSION ACCEPTED");
        setAccepted(true);

        return () => {
            setAccepted(false);
        }
    }, []);

    useEffect(() => {
        registerCallback("connection", "accepted", sessionAccepted);
    }, [registerCallback, sessionAccepted]);

    return (
        <ApiContext.Provider value={
            accepted ? { sendMessage, registerCallback } : null
        }>
            {children}
        </ApiContext.Provider>
    );
};

export { ApiContext, ApiProvider };

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

const ApiProvider = ({ children }) => {
    const session = useContext(SessionContext);
    const [connected, setConnected] = useState(false);
    const [accepted, setAccepted] = useState(false);
    const [ignoreUnknown, setIgnoreUnknown] = useState(true);
    
    const wsSendJsonRef = useRef(null);
    const dispatchRef = useRef({});

    const sendMessage = useCallback((type, event, data) => {
        if (!connected || !wsSendJsonRef.current) return;

        const message = {
            type,
            event,
            sessionId: session.sessionId,
            data: data ? data : {},
        };
        
        //console.log("Sending message", message);
        
        wsSendJsonRef.current(message);

    }, [connected, session?.sessionId]);

    const registerCallback = useCallback((type, event, handler) => {
        const key = `${type}:${event ? event : ''}`;
        dispatchRef.current[key] = handler;
    }, []);

    const unregisterCallback = useCallback((type, event, handler) => {
        const key = `${type}:${event ? event : ''}`;
        delete dispatchRef.current[key];
    }, []);

    const sessionAccepted = useCallback(() => {
        console.log("SESSION ACCEPTED");
        setAccepted(true);

        return () => {
            setAccepted(false);
        }
    }, []);

    const onConnected = useCallback((sendJson) => {
        // Immediately upon connection, send the connection request,
        // which should prompt a connection/accepted response
        setConnected(true);
        wsSendJsonRef.current = sendJson;
        sendMessage("connection", "connected");
    }, [setConnected, sendMessage])

    const onDisconnected = useCallback(() => {
        setConnected(false);
        setAccepted(false);
        wsSendJsonRef.current = null;
    }, [setConnected])

    useEffect(() => {
        registerCallback("connection", "accepted", sessionAccepted);
        return () => {
            unregisterCallback("connection", "accepted");
        }
    }, [registerCallback, unregisterCallback, sessionAccepted]);

    const dispatch = useCallback((message) => {
        if (!message) return;

        //console.log("Received message", message);

        const { type, event, data } = message;
        let handled = false;

        // For handlers that are specific to a type and event
        const type_event_key = `${type}:${event}`;
        if (dispatchRef.current[type_event_key]) {
            dispatchRef.current[type_event_key](data, type, event);
            handled = true;
        }

        // For handlers that are for all event of a type
        if (!handled) {
            const type_key = `${type}:`;
            if (dispatchRef.current[type_key]) {
                dispatchRef.current[type_key](data, type, event);
                handled = handled + 1;
            }
        }

        if (!handled && !ignoreUnknown) {
            console.warn("No handler for incoming message", message);
        }

        return () => {
            dispatchRef.current = {};
        }
    }, []);

    return (
        <ApiContext.Provider value={
            accepted ? {
                sendMessage,
                registerCallback,
                unregisterCallback,
                setIgnoreUnknown
            } : null
        }>
            {session?.sessionId ? <ApiWs 
                onConnected={onConnected}
                onDisconnected={onDisconnected}
                dispatch={dispatch}
            /> : <></>}
            {children}
        </ApiContext.Provider>
    );
};

const ApiWs = ({onConnected, onDisconnected, dispatch }) => {
    const [prevReadyState, setPrevReadyState] = useState(ReadyState.CONNECTING);

    const { sendJsonMessage, lastJsonMessage, readyState } = useWebSocket(
        WS_BASE, {
            share: false,
            shouldReconnect: () => true,
        },
    );

    useEffect(() => {
        if (prevReadyState !== readyState) {
            console.log("Connection state changed", readyState)
            setPrevReadyState(readyState);
        }

        if (readyState === ReadyState.OPEN) {
            console.log("WS connected");
            onConnected(sendJsonMessage);
        }
        if (readyState === ReadyState.CONNECTING || readyState === ReadyState.CLOSED) {
            console.log("WS disconnected");
            onDisconnected();
        }

        return () => {
            onDisconnected();
        }
    }, [
        onConnected, onDisconnected,
        readyState, sendJsonMessage,
        prevReadyState, setPrevReadyState,
    ]);

    useEffect(() => {
        if (!lastJsonMessage) return;
    
        dispatch(lastJsonMessage);
    }, [dispatch, lastJsonMessage])


    return ( <></> );
};

export { ApiContext, ApiProvider };

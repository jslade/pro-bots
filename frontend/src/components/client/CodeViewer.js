import React from 'react';
import { useParams } from 'react-router-dom';
import { ApiProvider } from '../../contexts/ApiContext';

const CodeViewer = () => {
    const params = useParams();

    return (
        <ApiProvider>
            <CodeViewerLayout name={params.name} />
        </ApiProvider>
    );

};

const CodeViewerLayout = ({ name }) => {
    return (
        <div>
            <h1>{name}</h1>

        </div> )
};

export default CodeViewer;
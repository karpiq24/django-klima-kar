import React, { useState, useRef, useEffect } from "react";
import PropTypes from "prop-types";

import InfiniteScroll from "react-infinite-scroller";

import Form from "react-bootstrap/Form";
import Popover from "react-bootstrap/Popover";
import Overlay from "react-bootstrap/Overlay";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPlusSquare, faTimes } from "@fortawesome/free-solid-svg-icons";

import ContentLoading from "./ContentLoading";
import "../../styles/infinite-select.css";

const InfiniteSelect = (props) => {
    const [search, setSearch] = useState("");
    const [selected, setSelected] = useState(props.selected);
    const [selectedLabel, setSelectedLabel] = useState(props.selectedLabel);
    const [show, setShow] = useState(false);
    const ref = useRef(null);

    const handleInputChange = (value) => {
        setSearch(value);
        props.refetch(value);
    };

    const selectOption = (value, label) => {
        setSelected(value);
        setSelectedLabel(label);
        setShow(false);
        props.onChange(value, label);
    };

    const handleOpenSelect = (event) => {
        setShow(!show);
    };

    useEffect(() => {
        const t = setTimeout(function () {
            if (selected === null || selected === undefined) setShow(props.show);
        }, 10);

        return () => {
            clearTimeout(t);
        };
    }, []);

    return (
        <div className={`infinite-select${show ? " is-open" : ""} ${props.className ? props.className : ""}`} ref={ref}>
            {props.label ? <Form.Label>{props.label}</Form.Label> : null}
            <div className="infinite-select-display" onClick={handleOpenSelect}>
                {selected && selectedLabel ? (
                    <div className="d-flex align-items-center">
                        {selectedLabel}
                        <FontAwesomeIcon
                            className="ml-2"
                            icon={faTimes}
                            onClick={(e) => {
                                e.stopPropagation();
                                selectOption(null, null);
                            }}
                        />
                    </div>
                ) : (
                    <div className="infinite-select-placeholder">{props.selectPlaceholder}</div>
                )}
            </div>
            <Overlay
                show={show}
                placement="bottom"
                container={ref.current}
                containerPadding={0}
                rootClose={true}
                onHide={() => setShow(false)}
            >
                <Popover>
                    <Popover.Content>
                        <div className="infinite-select-popup">
                            <Form.Control
                                autoFocus={props.autoFocus}
                                value={search}
                                onChange={(event) => handleInputChange(event.target.value)}
                                size="lg"
                                placeholder={props.searchPlaceholder}
                                className="infinite-select-search"
                            />
                            <hr />
                            <div className="infinite-select-results" key={search}>
                                <InfiniteScroll
                                    pageStart={1}
                                    loadMore={props.loadMore}
                                    hasMore={props.hasMore}
                                    useWindow={false}
                                    loader={<ContentLoading key="loading" />}
                                >
                                    {props.objects.length == 0 ? (
                                        props.onCreate ? (
                                            <div
                                                key="create-option"
                                                className="infinite-select-create"
                                                onClick={() => {
                                                    setShow(false);
                                                    props.onCreate(search);
                                                }}
                                            >
                                                <FontAwesomeIcon icon={faPlusSquare} />{" "}
                                                {props.createLabel ? props.createLabel : "Dodaj nowy"}
                                            </div>
                                        ) : (
                                            <div>Brak wyników</div>
                                        )
                                    ) : (
                                        props.objects.map((obj) => (
                                            <div
                                                key={obj.id}
                                                className="infinite-select-option"
                                                onClick={() => selectOption(obj.id, props.getObjectLabel(obj))}
                                            >
                                                {props.getObjectLabel(obj)}
                                            </div>
                                        ))
                                    )}
                                </InfiniteScroll>
                            </div>
                        </div>
                    </Popover.Content>
                </Popover>
            </Overlay>
        </div>
    );
};

InfiniteSelect.propTypes = {
    label: PropTypes.string,
    selectPlaceholder: PropTypes.string,
    searchPlaceholder: PropTypes.string,
    createLabel: PropTypes.string,
    onCreate: PropTypes.func,
    autoFocus: PropTypes.bool,
    show: PropTypes.bool,
    loadMore: PropTypes.func.isRequired,
    hasMore: PropTypes.bool.isRequired,
    objects: PropTypes.array.isRequired,
    getObjectLabel: PropTypes.func.isRequired,
    selected: PropTypes.string,
    selectedLabel: PropTypes.string,
    onChange: PropTypes.func,
    className: PropTypes.string,
    required: PropTypes.bool,
};

export default InfiniteSelect;

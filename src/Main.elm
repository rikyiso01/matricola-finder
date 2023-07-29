module Main exposing (..)

import Browser exposing (sandbox)
import Data exposing (data)
import Html exposing (Html, div, h1, i, input, label, main_, table, tbody, td, text, th, thead, tr)
import Html.Attributes exposing (class, for, id, type_, value)
import Html.Events exposing (onInput)
import List exposing (all, filter, head, map, tail)
import Maybe exposing (withDefault)
import String exposing (contains, fromList, join, split, toList, toLower)


main : Program () Model Msg
main =
    sandbox { init = init, update = update, view = view }


type alias Model =
    { search : String
    }


type alias Student =
    { name : String, matricola : String }


init : Model
init =
    { search = "" }


type Msg
    = Change String


update : Msg -> Model -> Model
update msg model =
    case msg of
        Change new_search ->
            { model | search = new_search }


view : Model -> Html Msg
view model =
    main_ [ class "responsive" ]
        [ h1 [] [ text "Matricola Finder" ]
        , div [ class "field", class "label", class "prefix", class "border" ]
            [ i [] [ text "search" ]
            , input [ type_ "text", id "search", value model.search, onInput Change ] []
            , label [ for "seach" ] [ text "Cerca" ]
            ]
        , table [ class "border" ]
            [ thead []
                [ tr []
                    [ th [] [ text "Nome" ]
                    , th [] [ text "Matricola" ]
                    ]
                ]
            , tbody [] (map row (filter (rowFilter model) data))
            ]
        ]


rowFilter : Model -> Student -> Bool
rowFilter model student =
    all (\keyword -> contains keyword student.name || contains keyword student.matricola) (map toLower (split " " model.search))


capitalize : String -> String
capitalize string =
    join " " (map capitalizeWord (split " " string))


capitalizeWord : String -> String
capitalizeWord word =
    let
        word_list =
            toList word
    in
    fromList
        (case head word_list of
            Just char ->
                Char.toUpper char :: withDefault [] (tail word_list)

            Nothing ->
                []
        )


row : Student -> Html Msg
row data =
    tr []
        [ td [] [ text (capitalize data.name) ]
        , td [] [ text data.matricola ]
        ]

import React from "react";
import Draggable, {DraggableProps} from "react-draggable";
import Card, {CardState} from "./Card";

export function DraggableBoard({cards, setCards, ...props}: {cards: CardState[], setCards: (cards: CardState[]) => void}) {
  function onDragStop (this: DraggableProps, e: any, data: any) {
    e.preventDefault();

    const cardIx = cards.findIndex(
      card => card.id === (this.children as any)?.props?.card?.id
    )
    console.log('cardId', cardIx, (this.children as any)?.props?.id)
    if (cardIx >= 0) {
      const card = cards[cardIx]
      // card.position = {x: data.x, y: data.y}
      const newCards = [
        ...cards.slice(0, cardIx),
        ...cards.slice(cardIx + 1),
        card,
      ]
      setCards(newCards)
      console.log(newCards)
    }
    console.log('onDragStop', e, this, data)

  }
  return (
    <div {...props} >
      {
        cards.map((card) => (
          <Draggable
            onStop={onDragStop}
            // position={card.position}
            // defaultPosition={card.position}
            // positionOffset={{x: 0, y: 0}}
            key={card.id}
          >
            <Card
              className={`card ${card.picture ? 'picture' : 'word'}`}
              card={card}
            />
          </Draggable>
        ))}
    </div>
  );
}

import React from "react";


export type CardState = {
  id: string,
  word: string,
  picture?: string,
  selected?: boolean,
  hidden?: boolean,
  shake?: boolean,
  // sound?: string,
  // position: {x: number, y: number},
  // order: number,
}

export default function Card({card, ...props}: any) {
  props.className = `card ${card.picture ? 'picture' : 'word'} ${props.className || ''}`
  return (
      <div {...props} >
        {card.picture?
              <img src={card.picture} alt={card.id} onDragStart={(e)=> e.preventDefault()}/>
              :
              <span>{card.word}</span>
            }
      </div>
  );
}

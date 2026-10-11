#pragma once
namespace stationCollectionCorners {
// Folder kind is stable when visible positions change after filtering or sorting.
constexpr bool allGamesKind(int kind){return kind==2;}
constexpr bool squareCollection(bool systems,bool folders,bool allGames=false){return systems&&folders&&!allGames;}
constexpr float radius(bool systems,bool folders,float w,float h,bool allGames=false){
 // All-games keeps the platform contour, focused or adjacent. Actual collections
 // stay square. Individual game covers retain their existing shape.
 return (w<h?w:h)*(systems&&!squareCollection(systems,folders,allGames)?.115f:0.f);
}
}

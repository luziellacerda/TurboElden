#pragma once
namespace stationCollectionCorners {
constexpr bool squareCollection(bool systems,bool folders){return systems&&folders;}
constexpr float radius(bool systems,bool folders,float w,float h){
 // Every collection screen: live video, cached poster, placeholder and touch contour.
 // Main platforms retain their current radius. Individual games remain unchanged.
 return (w<h?w:h)*(systems&&!squareCollection(systems,folders)?.115f:0.f);
}
}

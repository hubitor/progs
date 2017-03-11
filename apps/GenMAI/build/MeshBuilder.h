#ifndef MESHER_H
#define MESHER_H

#include <vector>
#include "Point.h"
#include "Element.h"
#include "MeshParameters.h"
#include "Builder.h"
class Mesh;

/**
 * @brief Fills a Mesh with the description of a horizontal sheet of metal.
 *        2D Quad elements are used. The mesh is described as a set of Layers.
 *        Parameters are defined in a MeshParameters object.
 */

class MeshBuilder : public Builder
{
    Mesh &target;
    MeshParameters par;

public:
    MeshBuilder(Mesh &_target);

    void         setParameters(const MeshParameters &p);
    virtual void printParameters() const;
    virtual void genere();

private:
    double currentHeight;        ///< ordonnee courante
    double dx;                   ///< largeur des mailles courantes
    int    first;                ///< no du premier noeud de la ligne
    int    last;                 ///< no du dernier noeud de la ligne

    double computeBoundaryHeight();
    double computeReductionFactor();
    void meshFirstLine();
    void meshGradient();
    void meshGradientLayer(int lev);
    double getGradientDelta(int lev);
    void meshBoundary();
    void meshReductionLayer();
    void addReductionNodes();
    void addReductionElements();
    void meshConstantLayer();
    void addConstantNodes();
    void addConstantElements();
    void setContactNodes(int first, int last);
    void increaseHeight(double dh);
    void Initialize();
};

#include "MeshBuilder.inl"

#endif

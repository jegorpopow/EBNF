start:
  <S>;
names:
 $l := "(";
 $r := ")";
rules:
  <S> := ((EPS) | ($l <S> $r <S>));

